import scrib_constants as constants

from ast.globel.globalcontinue import (
    traverse_continue as globalcontinue_traverse_continue,
    get_label_child as globalcontinue_get_label_child
)

from ast.local.localnode import LocalNode as LocalNode


class LocalContinue(LocalNode):
    #reclab = None  # String

    def __init__(self, local_role, reclab):
        super(LocalContinue, self).__init__(local_role)
        self.reclab = reclab

    def get_label(self):
        return self.reclab

    def pretty_print(self):
        return constants.CONTINUE_KW + ' ' + self.get_label() + ';'

    def context_visitor_enter(self, cv):
        context_ = cv.get_context()
        contlab = context_.get_current_scope() + '.' + self.get_label()
        clone = context_.add_continue_label(contlab) 
        #clone = clone.set_rec_exitable(False)
        clone = clone.set_cont_exitable(False)
        cv.set_context(clone)
    
    def context_visitor_visit(self, cv):
        return self
    
    def context_visitor_leave(self, cv):
        pass


def traverse(traverser, node_):
    return globalcontinue_traverse_continue(traverser, node_,
                                            get_label_child(node_));


def get_label_child(node):
    return globalcontinue_get_label_child(node)
