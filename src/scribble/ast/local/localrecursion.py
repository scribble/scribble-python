import scrib_constants as constants
import scrib_util as util

from ast.globel.globalrecursion import (
    traverse_recursion as globalrecursion_traverse_recursion,
    get_label_child as globalrecursion_get_label_child,
    get_block_child as globalrecursion_get_block_child
)

from ast.local.localnode import LocalNode as LocalNode


#LABEL_INDEX = 0
#BLOCK_INDEX = 1


class LocalRecursion(LocalNode):
    #reclab = None # String
    #block = None  # localprotocolblock

    def __init__(self, local_role, reclab, block):
        super(LocalRecursion, self).__init__(local_role)
        self.reclab = reclab
        self.block = block

    def get_label(self):
        return self.reclab

    # rename to get_block to be more uniform
    def get_block_child(self):
        return self.block

    def pretty_print(self):
        text = ""
        text = text + constants.REC_KW + ' ' + self.get_label() + '\n'
        text = text + self.get_block_child().pretty_print()
        return text

    def context_visitor_enter(self, cv):
        context_ = cv.get_context()
        pushed = context_.push_localrecursion(self)
        cv.set_context(pushed)
    
    def context_visitor_visit(self, cv):
        return self.visit(cv)
    
    def context_visitor_leave(self, cv):
        context_ = cv.get_context()
        reclab = context_.get_current_scope() + '.' + self.get_label()
        context_ = context_.remove_recursion_label(reclab)
        if context_.is_continue_label_seen(reclab):
            context_ = context_.remove_continue_label(reclab);
        context_ = context_.set_rec_exitable(context_.get_cont_exitable()) 
        cv.set_context(context_.pop_localrecursion(self))

    def visit(self, visitor):
        lab = self.get_label()
        block = self.get_block_child()
        visited = visitor.visit(block)
        return visitor.nf.localrecursion(self.local_role, lab, visited)


def traverse(traverser, node_):
    return globalrecursion_traverse_recursion(traverser, node_,
                                              get_label_child(node_),
                                              get_block_child(node_))


def get_label_child(node_):
    #return node_.getChild(LABEL_INDEX)
    return globalrecursion_get_label_child(node_)

def get_block_child(node_):
    #return node_.getChild(BLOCK_INDEX)
    return globalrecursion_get_block_child(node_)
