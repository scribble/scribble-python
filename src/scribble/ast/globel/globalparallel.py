import scrib_collections as collections
import scrib_constants as constants
import scrib_util as util

from ast.globel.globalprotocolblock import \
    pretty_print as globalprotocolblock_pretty_print


def traverse_parallel(traverser, node_, blocks):
    traversed = []
    for block in blocks:
        traversed.append(traverser.traverse(block))
    return util.antlr_dupnode_and_replace_children(node_, traversed)

def traverse(traverser, node_):
    return traverse_parallel(traverser, node_,
                            get_block_children(node_))


# Duplicated from globalchoice
def _context_visit_children_and_cache_contexts(cv, node_):
    blocks = get_block_children(node_) # [node_]
    visited = []
    contexts = []  # From visiting each block
    for block in blocks:
        clone = cv.clone()  # Factor out?
        # Section 4.6.6 -- well-formed choice blocks
        visited.append(clone.visit(block)) 
        contexts.append(clone.get_context())
    dup = util.antlr_dupnode_and_replace_children(node_, visited)
    dup.cachedContexts = contexts
    return dup
    
def _peek_cached_contexts(node_):
    return node_.cachedContexts

def _remove_cached_contexts(node_):
    contexts = node_.cachedContexts
    node_.cachedContexts = None
    return contexts


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    pushed = context_.push_globalparallel(node_)
    cv.set_context(pushed)


def context_visitor_visit(cv, node_):
    return _context_visit_children_and_cache_contexts(cv, node_)


# Update context according to rules for parallel
def context_visitor_leave(cv, node_):
    clone = cv.get_context().clone()
        # Still the originally pushed context for this parallel (each child was
        # visited with a cloned visitor)
    contexts = _remove_cached_contexts(node_)

    # Section 4.6.8 -- potential operators and sig parameters
    ops = collections.clone_collection(contexts[0].get_operators())
        # includes sig parameters
    for c in contexts[1:]:
        tmp = c.get_operators()
        for (src, dest) in tmp.keys():
            if (src, dest) in ops.keys():
                ops[(src, dest)] |= tmp[(src, dest)]  # set union
            else:
                ops[(src, dest)] = tmp[(src, dest)]

    # Need to do this kind of manual child Context merging every time we process
    # multiple children subcontexts. don't need to do for e.g. recursion (single
    # child subcontext)

    # Add all operators and sig parameters seen in children for each src/dest pair
    for (src, dest) in ops.keys():
        for op in ops[(src, dest)]:
            if not clone.is_operator_seen(src, dest, op):
                clone = clone.add_operator(src, dest, op)

    # Add all operators and sig parameters from parent Context for each src/dest
    # pair
    prev = clone.parent.get_operators()
    for (src, dest) in prev.keys():
        for op in prev[(src, dest)]:
            if not(clone.is_operator_seen(src, dest, op)):
                clone = clone.add_operator(src, dest, op)

    # TODO: Parallel deadlocks not specified in langref (maybe should not be)
    seen = set([])  # Only for used here for checking deadlocks
    for (src, dest) in clone.get_operators().keys():
        if (dest, src) in seen:  # too coarse grained?
            #print '[Warning] Potential deadlock: ', src, dest
                # FIXME: false positive on A -> B; par { B -> A } -- clearing
                # operators on par entry would fix this, but may break something
                # else
            pass 
        seen.add((src, dest))

    # Add all enabled role and initial operators (Section 4.6.6) seen in children
    # for each src/dest pair
    current = clone.get_enabled_roles()
    for c in contexts:
        for role, ops in c.get_enabled_roles().items():
            for op in ops:
                # Need enabling ops from all par blocks
                #if not(clone.is_role_enabled(role)): 
                clone = clone.enable_role(role, op)

    # recLabs no modifications
    
    for c in contexts:
        for lab in c.get_continue_labels():
            clone = clone.add_continue_label(lab)

    rec_exitable = True
    for c in contexts:
        if not c.get_rec_exitable(): 
            # TODO: currently any non-rec_exitable child makes the whole parallel
            # non-rec_exitable. However, this should actually be role-sensitive,
            # e.g. par { rec X A->B. X } and { C->D} C->D. "rec_exitable" will be
            # replaced by local projection reachability
            rec_exitable = False
            break
    clone = clone.set_rec_exitable(rec_exitable)

    do_exitable = True
    for c in contexts:
        if not c.get_do_exitable(): 
            do_exitable = False
            break
    clone = clone.set_do_exitable(do_exitable)

    for c in contexts:
        for contLab in c.get_continue_labels():
            clone = clone.add_continue_label(contLab)

    # Duplicated from globalchoice
    scopes = clone.get_current_scopes()
    new = []
    for c in contexts:
        for scope in c.get_current_scopes() - scopes:
            if scope in new:
                util.report_error("Bad scope: " + scope)
            new.append(scope)
            clone = clone.add_scope(scope)

    cv.set_context(clone.pop_globalparallel(node_))


def check_wellformedness_enter(checker, node_):
    pass


# Semantics of parallel: if thread1:A!B(l1) is dispatched before
# thread2:A!B(l2), then l1 will arrive before l2 (ordered delivery between each
# directed pair of roles, what parallel means is that the dispatch before
# delivery is unordered) -- this doesn't match the old trace semantics though
# (does it?)
#
# Adapted from globalchoice
def check_wellformedness_visit(checker, node_):
    context = checker.get_context()
    visited = _context_visit_children_and_cache_contexts(checker, node_)
    contexts = _peek_cached_contexts(visited)

    # Section 4.6.8 -- potential operators and sig parameters
    ops = collections.clone_collection(contexts[0].get_operators())
        # includes sig parameters
    for c in contexts[1:]:
        tmp = c.get_operators()
        for (src, dest) in tmp.keys():
            if (src, dest) in ops.keys():
                us = ops[(src, dest)]
                them = tmp[(src, dest)]
                # Section 4.6.8 -- potential operators and parameters disjoint
                # between each block
                if not us.isdisjoint(them):
                    util.report_error("Bad parallel operator(s): " + \
                                      str(us & them))
                ops[(src, dest)] = us | them  # set union
            else:
                ops[(src, dest)] = tmp[(src, dest)]

    return visited


def check_wellformedness_leave(checker, node_):
    # Context was updated and set at the end of the check_wellformedness_visit
    pass


def project(projector, node_):
    blocks = []
    for block in get_block_children(node_):
        tmp = projector.visit(block)
        if not tmp.is_empty():
            blocks.append(tmp)
    if blocks:
        return projector.nf.localparallel(#projector.rolemap[projector.role],
                                          projector.role,
                                          blocks)
    else:
        return None


def get_block_children(node_):
    return node_.getChildren()


def pretty_print(node_):
    text = constants.PAR_KW + '\n'
    blocks = get_block_children(node_)
    text = text + globalprotocolblock_pretty_print(blocks[0])
    for block in blocks[1:]:
        text = text + constants.AND_KW + '\n'
        text = text + globalprotocolblock_pretty_print(block)
    return text
