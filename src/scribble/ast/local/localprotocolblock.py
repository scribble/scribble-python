import scrib_util as util

from ast.local.localnode import LocalNode as LocalNode

from ast.local.localinteractionsequence \
    import pretty_print as localinteractionsequence_pretty_print
    
"""from ast.globel.globalprotocolblock import (
    context_visitor_enter as globalprotocolblock_context_visitor_enter,
    context_visitor_visit as globalprotocolblock_context_visitor_visit,
    context_visitor_leave as globalprotocolblock_context_visitor_leave
)"""


SEQUENCE_INDEX = 0


class LocalProtocolBlock(LocalNode):
    #seq = None   # localinteractionsequence

    def __init__(self, local_role, seq):
        super(LocalProtocolBlock, self).__init__(local_role)
        self.seq = seq

    # FIXME: fix name
    def get_localinteraction_sequence(self):
        return self.seq

    def is_empty(self):
        seq = self.get_localinteraction_sequence()
        return not seq.get_children()

    def pretty_print(self):
        return '{\n' + self.get_localinteraction_sequence().pretty_print() + \
               '\n}'

    def context_visitor_enter(self, cv):
        cv.enter(self)
    
    def context_visitor_visit(self, cv):
        return self.visit(cv)
    
    def context_visitor_leave(self, cv):
        cv.leave(self)

    def visit(self, visitor):
        seq = self.get_localinteraction_sequence()
        visited = visitor.visit(seq)
        return visitor.nf.localprotocolblock(self.local_role, visited)


def traverse(traverser, node_):
    sequence = get_localinteractionsequence_child(node_)
    traversed = [traverser.traverse(sequence)]
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def pretty_print(node_):
    text = '{\n'
    children = get_localinteractionsequence_child(node_)
    text = text + localinteractionsequence_pretty_print(children)
    text = text + '\n}'
    return text


def get_localinteractionsequence_child(node_):
    return node_.getChild(SEQUENCE_INDEX)


"""def context_visitor_enter(cv, node_):
    globalprotocolblock_context_visitor_enter


def context_visitor_visit(cv, node_):
    return globalprotocolblock_context_visitor_visit


def context_visitor_leave(cv, node_):
    globalprotocolblock_context_visitor_leave


def check_reachability_enter(checker, node_):
    pass


def check_reachability_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_reachability_leave(checker, node_):
    pass"""
