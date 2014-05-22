import scrib_constants as constants
import scrib_util as util

from ast.globel.globalchoice import (
    traverse_choice as globalchoice_traverse_choice,
    get_subject_child as globalchoice_get_subject_child,
    get_block_children as globalchoice_get_block_children
)

from ast.local.localnode import LocalNode as LocalNode


class LocalChoice(LocalNode):
    #subject = None  # String
    #blocks = None # List of localprotocolblock

    def __init__(self, local_role, subject, blocks):
        super(LocalChoice, self).__init__(local_role)
        self.subject = subject
        self.blocks = blocks

    def get_subject(self):
        return self.subject

    def get_block_children(self):
        return self.blocks

    def pretty_print(self):
        blocks = self.get_block_children()
        text = constants.CHOICE_KW + ' ' + constants.AT_KW
        text = text + ' ' + self.get_subject() + '\n'
        text = text + blocks[0].pretty_print()
        for block in blocks[1:]:
            text = text + '\n' + constants.OR_KW + '\n'
            text = text + block.pretty_print()
        return text

    def context_visitor_enter(self, cv):
        context_ = cv.get_context()
        pushed = context_.push_localchoice(self)
        cv.set_context(pushed)

    def context_visitor_visit(self, cv):
        blocks = self.get_block_children()
        visited = []
        contexts = []
        for block in blocks:
            clone = cv.clone()
            visited.append(clone.visit(block))
            contexts.append(clone.get_context())
        self._cached_contexts = contexts
        return cv.nf.localchoice(self.local_role, self.get_subject(), visited)

    def context_visitor_leave(self, cv):
        context_ = cv.get_context()
        contexts = self._cached_contexts
    
        for c in contexts:
            for lab in c.get_continue_labels():
                context_ = context_.add_continue_label(lab)
        
        rec_exitable = True
        for c in contexts:
            if not c.get_rec_exitable(): 
                rec_exitable = False
                break
        context_ = context_.set_rec_exitable(rec_exitable)

        cont_exitable = False
        for c in contexts:
            if c.get_cont_exitable(): 
                cont_exitable = True
                break
        context_ = context_.set_cont_exitable(cont_exitable)
    
        do_exitable = True
        for c in contexts:
            if not c.get_do_exitable(): 
                do_exitable = False
                break
        context_ = context_.set_do_exitable(do_exitable)
        
        popped = context_.pop_localchoice(self)
        cv.set_context(popped)

    def visit(self, visitor):
        blocks = self.get_block_children()
        visited = []
        for block in blocks:
            visited.append(visitor.visit(block))
        return visitor.nf.localchoice(self.local_role,
                                      self.get_subject(),
                                      visited)


def traverse(traverser, node_):
    return globalchoice_traverse_choice(traverser, node_,
                                        get_subject_child(node_),
                                        get_block_children(node_))


def get_subject_child(node_):
    return globalchoice_get_subject_child(node_)

def get_block_children(node_):
    return globalchoice_get_block_children(node_)
