import scrib_util as util


def traverse(traverser, node_):
    traversed = []
    for child in get_children(node_):
        next = traverser.traverse(child)
        traversed.append(next)
    return util.antlr_dupnode_and_replace_children(node_, traversed)


"""def _context_visit_children_and_cache_contexts(cv, node_):
    visited = []
    contexts = []  # From visiting each block
    for child in get_children(node_):
        visited.append(cv.visit(child))
        contexts.append(cv.get_context().clone())
    dup = util.antlr_dupnode_and_replace_children(node_, visited)
    dup._cachedContexts = contexts
    return dup
    
def _peek_cached_contexts(node_):
    return node_._cachedContexts

def _remove_cached_contexts(node_):
    contexts = node_._cachedContexts
    node_._cachedContexts = None
    return contexts"""


def context_visitor_enter(cv, node_):
    cv.enter(node_)


def context_visitor_visit(cv, node_):
    #return _context_visit_children_and_cache_contexts(cv, node_)
    visited = []
    for child in get_children(node_):
        visited.append(cv.visit(child))
    return util.antlr_dupnode_and_replace_children(node_, visited)


def context_visitor_leave(cv, node_):
    cv.leave(node_)


def check_wellformedness_enter(checker, node_):
    pass


def check_wellformedness_visit(checker, node_):
    visited = []
    for child in get_children(node_):
        context_ = checker.get_context()
        #if not context_.has_exit():
        #    util.report_error("Bad sequence: " + util.pretty_print(child))
            # Check moved to local projections
        # Section 4.6.4 -- Well-formed global interactions
        visited.append(checker.visit(child))
    return util.antlr_dupnode_and_replace_children(node_, visited)


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    projected = []
    for child in get_children(node_):
        tmp = projector.visit(child)
        if tmp is not None:
            projected.append(tmp)
    local = projector.nf.localinteractionsequence(
                #projector.rolemap[projector.role], projected)
                projector.role, projected)
    return local


def get_children(node_):
    return node_.getChildren()


def pretty_print(node_):
    text = ""
    children = get_children(node_)
    if children:
        text = text + util.pretty_print(children[0])
        for child in children[1:]:
               text = text + '\n' + util.pretty_print(child)
    return text
