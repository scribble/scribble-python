import scrib_util as util

from ast.globel.globalinteractionsequence import \
    pretty_print as globalinteractionsequence_pretty_print


SEQUENCE_INDEX = 0


def traverse(traverser, node_):
    sequence = get_globalinteractionsequence_child(node_)
    traversed = [traverser.traverse(sequence)]
    rebuilt = util.antlr_dupnode_and_replace_children(node_, traversed)
    return rebuilt


def context_visitor_enter(cv, node_):
    cv.enter(node_)


def context_visitor_visit(cv, node_):
    sequence = get_globalinteractionsequence_child(node_)
    visited = [cv.visit(sequence)]
    return util.antlr_dupnode_and_replace_children(node_, visited)


def context_visitor_leave(cv, node_):
    cv.leave(node_)


def check_wellformedness_enter(checker, node_):
    pass


def check_wellformedness_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    seq = projector.visit(get_globalinteractionsequence_child(node_))
    local = projector.nf.localprotocolblock(#projector.rolemap[projector.role],
                                            projector.role,
                                            seq)
    return local


def pretty_print(node_):
    text = '{\n'
    child = get_globalinteractionsequence_child(node_)
    text = text + globalinteractionsequence_pretty_print(child)
    text = text + '\n}'
    return text


def get_globalinteractionsequence_child(node_):
    return node_.getChild(SEQUENCE_INDEX)
