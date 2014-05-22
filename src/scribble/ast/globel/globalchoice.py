import scrib_collections as collections
import scrib_constants as constants
import scrib_util as util

from ast.role import get_role_name as role_get_name

from ast.globel.globalprotocolblock import \
    pretty_print as globalprotocolblock_pretty_print


DUMMY_ENABLING_OP = '_DUMMY_ENABLING_OP'


SUBJECT_INDEX = 0
BLOCKS_START_INDEX = 1


def traverse_choice(traverser, node_, subject, blocks):
    traversed = []
    traversed.append(traverser.traverse_untyped_leaf(subject))
    for block in blocks:
        traversed.append(traverser.traverse(block))
    return util.antlr_dupnode_and_replace_children(node_, traversed)

def traverse(traverser, node):
    return traverse_choice(traverser, node, get_subject_child(node),
                           get_block_children(node))


# Similar to traverse, but visit each block with a separate context (visitor
# clones) (and not supported for every node)
def _context_visit_children_and_cache_contexts(cv, node_):
    blocks = get_block_children(node_) # [node_]
    visited = []
    contexts = []  # From visiting each block
    visited.append(get_subject_child(node_))
    for block in blocks:
        clone = cv.clone()
        # Section 4.6.6 -- well-formed choice blocks
        visited.append(clone.visit(block))
        contexts.append(clone.get_context())
    dup = util.antlr_dupnode_and_replace_children(node_, visited)
    dup._cachedContexts = contexts
    return dup
    
def _peek_cached_contexts(node_):
    return node_._cachedContexts

def _remove_cached_contexts(node_):
    contexts = node_._cachedContexts
    node_._cachedContexts = None
    return contexts


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    pushed = context_.push_globalchoice(node_) 
        # Clears enabledroles map for visiting this choice
    cv.set_context(pushed)
    

def context_visitor_visit(cv, node_):
    return _context_visit_children_and_cache_contexts(cv, node_)

 
# Update Context (i.e. the info recorded to check well-formedness of each
# construct) according to rules for choice
#
# Still need to break into smaller routines and some can be factored out with
# parallel
#
# Some should go in Context.pop_globalchoice? (would be better for modifying some
# fields directly)
def context_visitor_leave(cv, node_):
    # Still the "original context" on entering the Choice (not yet updated with
    # any information from visiting block children)
    #
    # Perhaps instead clone the parent context (the context before entering this
    # choice)?
    clone = cv.get_context().clone()
    subj = get_subject(node_)  # string

    contexts = _remove_cached_contexts(node_)

    # Update enabled roles (initial ops) map (Section 4.6.6 -- initial operators)
    prev = clone.parent.get_enabled_roles()

    # Get information from parent context (enabledroles was originally cleared
    # by push_globalchoice to visit this choice)
    #
    # Can factor out to sequencing? Maybe not: this is an instance of generally
    # carrying information over from the parent context, not just sequencing
    # sitations
    ##clone._enabled_roles = {}  # HACK (1)
    for role_, ops in prev.items():
        for op in ops:
            # Carry "initial ops" over from parent context
            clone = clone.enable_role(role_, op)

    # Update context with information from visiting this choice's blocks
    enabled = collections.clone_collection(contexts[0].get_enabled_roles())
    for c in contexts[1:]:
        tmp = c.get_enabled_roles()
        for role_, ops in tmp.items():
            if role_ != subj:
                enabled[role_] |= ops
    for role_, ops in enabled.items():
        # We only want the "intial ops", so if role_ was already enabled before
        # this choice, we don't need to record the ops we saw here
        if role_ not in prev.keys():
            for op in ops:
                clone = clone.enable_role(role_, op)

    # Update potental operators (Section 4.6.8) map
    #
    # N.B. "potential operators" for parallel well-formedness; not "enabling
    # operators" (already treated above)
    potops = clone.get_operators()
    for c in contexts:
        # New potential operators from visiting blocks, add them all to the
        # existing map
        for (src, dest), ops in c.get_operators().items():
            for op in ops:
                if (src, dest) not in potops.keys() or op not in potops[(src, dest)]:
                    # need to collect all operators (for parallel check) from
                    # each choice block as a set
                    clone = clone.add_operator(src, dest, op)

    #Update reclabs? -- no: don't need to do reclabs because any in-scope
    #contlab should have been declared in an outer context; any contlab declared
    #inside the choice cannot possibly be carried over here
    
    for c in contexts:
        for lab in c.get_continue_labels():
            clone = clone.add_continue_label(lab)

    # Reachability and (tail) recursion checks -- this needs to be revised to
    # properly conform to the langref
    rec_exitable = False  # "Possibly exitable": choice has an exit
    for c in contexts:
        if c.get_rec_exitable(): 
            rec_exitable = True
            break
    clone = clone.set_rec_exitable(rec_exitable)

    do_exitable = True
    for c in contexts:
        if not c.get_do_exitable(): 
            do_exitable = False
            break
    clone = clone.set_do_exitable(do_exitable)

    for c in contexts:
        for contlab in c.get_continue_labels():
            clone = clone.add_continue_label(contlab)

    scopes = clone.get_current_scopes()
    new = []
    for c in contexts:
        for scope in c.get_current_scopes() - scopes:
            if scope in new:
                util.report_error("Bad scope: " + scope)
            new.append(scope)
            clone = clone.add_scope(scope)

    cv.set_context(clone.pop_globalchoice(node_))


def check_wellformedness_enter(checker, node_):
    context = checker.get_context()
    # Section 4.6.6 -- at-role of choice is bound
    #
    # This condition needs to be checked here before performing the
    # choice-specific Context push
    subj = get_subject(node_)
    if not context.is_role_declared(subj):
        util.report_error("Bad choice subject: " + subj)
    if not context.is_role_enabled(subj):
        util.report_error("Choice subject not enabled: " + subj)


# (A->B or A->C;C->B); A->C would be OK with the right labels
#
# (A->B;C->A:l1;B->C:l2 or A->B;C->A:l1;B->C:l3) -- C not initially enabled but
# equal until enabled (and cannot be factored out)
def check_wellformedness_visit(checker, node_):
    #context_ = checker.get_context()
    visited = _context_visit_children_and_cache_contexts(checker, node_)
    contexts = _peek_cached_contexts(visited)
    subj = get_subject(visited)         # string

    # Here we first do the checks involving just the information collected from
    # this choice (push_globalchoice clears enabledroles). Information from
    # parent is carried over to the new context later below.
    #
    # Map from role_ name (string) to set of enabling op (Section 4.6.6 --
    # initial operators) names (strings) -- values set in globalmessagetransfer
    enabled = collections.clone_collection(contexts[0].get_enabled_roles())
    for c in contexts[1:]:
        tmp = c.get_enabled_roles()
        # Section 4.6.6 -- same set of roles occur in each block
        if set(tmp.keys()) != set(enabled.keys()):
            util.report_error("Bad choice block: " + ' '
                             + str(enabled.keys()) + str(tmp.keys()))
                             # + "\n" + util.pretty_print(c.getnode()))
        for role_, ops in tmp.items():
            #if not(ops == None):
            if role_ != subj:
                # Should be generalised for all roles that are already enabled,
                # not just the subject?  # No: already taken care of by the fact
                # that enabled records only the initial enabling ops (added in
                # globalmessagetransfer), not all operators  # So here maybe
                # better to use "if not enabled"?
                for op in ops:
                    # Section 4.6.6 -- initial operators in each block for each
                    # role_ are disjoint
                    if op in enabled[role_] and \
                            op != DUMMY_ENABLING_OP:  # HACK (1)?
                        util.report_error("Bad choice operator: " + op)
                    enabled[role_].add(op)
    return visited


def check_wellformedness_leave(checker, node_):
    pass  # Context updated and set by context_visitor_leave


# choice at A { A->B; B->C } projected for C to choice at A { C?B } doesn't make
# much sense
def project(projector, node_):
    subject = get_subject(node_)
    blocks = []
    for block in get_block_children(node_):
        tmp = projector.visit(block)
        if not tmp.is_empty():
            blocks.append(tmp)
    if subject == projector.role or blocks: 
        # if subject, then blocks guaranteed non-empty by well-formedness
        return projector.nf.localchoice(#projector.rolemap[projector.role],
                                        projector.role,
                                        #projector.rolemap[subject],
                                        subject,
                                        blocks)
    else:
        return None


def get_subject(node_):
    return role_get_name(get_subject_child(node_))


def pretty_print(node_):
    blocks = get_block_children(node_)
    text = constants.CHOICE_KW + ' ' + constants.AT_KW + ' ' + get_subject(node_)
    text = text + '\n' + globalprotocolblock_pretty_print(blocks[0])
    for block in blocks[1:]:
        text = text + '\n' + constants.OR_KW + '\n'
        text = text + globalprotocolblock_pretty_print(block)
    return text


def get_subject_child(node_):
    return node_.getChild(SUBJECT_INDEX)

def get_block_children(node_):
    return node_.getChildren()[BLOCKS_START_INDEX:]
