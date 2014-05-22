import scrib_util as util

from ast.local.localnode import LocalNode as LocalNode

"""from ast.globel.globalinteractionsequence import (
    context_visitor_enter as globalinteractionsequence_context_visitor_enter,
    context_visitor_visit as globalinteractionsequence_context_visitor_visit,
    context_visitor_leave as globalinteractionsequence_context_visitor_leave
)"""


class LocalInteractionSequence(LocalNode):
    #children  = None   # List of localnode (from a subset of localnode)

    def __init__(self, local_role, children):
        super(LocalInteractionSequence, self).__init__(local_role)
        self.children = children

    def get_children(self):
        return self.children

    def pretty_print(self):
        text = ""
        children = self.get_children()
        if children:
            text = text + children[0].pretty_print()
            for child in children[1:]:
                text = text + '\n'
                text = text + child.pretty_print()
        return text

    def context_visitor_enter(self, cv):
        cv.enter(self)
    
    def context_visitor_visit(self, cv):
        return self.visit(cv)
    
    def context_visitor_leave(self, cv):
        cv.leave(self)

    def check_reachability_visit(self, checker):
        visited = []
        for child in self.get_children():
            context_ = checker.get_context()
            if not context_.has_exit():
                util.report_error("Bad sequence: " + child.pretty_print())
            visited.append(checker.visit(child))
        return checker.nf.localinteractionsequence(self.local_role, visited)

    def visit(self, visitor):
        visited = []
        for child in self.get_children():
            visited.append(visitor.visit(child))
        return visitor.nf.localinteractionsequence(self.local_role, visited)


def traverse(traverser, node_):
    traversed = []
    for child in get_children(node_):
        next = traverser.traverse(child)
        traversed.append(next)
    rebuilt = util.antlr_dupnode_and_replace_children(node_, traversed)
    return rebuilt


def pretty_print(node_):
    text = ""
    children = get_children(node_)
    if children:
        text = text + util.pretty_print(children[0])
        for child in children[1:]:
            text = text + '\n'
            text = text + util.pretty_print(child)
    return text


def get_children(node_):
    return node_.getChildren()


"""
def context_visitor_enter(cv, node_):
    globalinteractionsequence_context_visitor_enter(cv, node_)


def context_visitor_visit(cv, node_):
    return globalinteractionsequence_context_visitor_visit(cv, node_)


def context_visitor_leave(cv, node_):
    globalinteractionsequence_context_visitor_leave(cv, node_)


def check_reachability_enter(checker, node_):
    pass


def check_reachability_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_reachability_leave(checker, node_):
    pass"""
