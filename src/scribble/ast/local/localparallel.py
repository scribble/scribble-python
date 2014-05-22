import scrib_constants as constants
import scrib_util as util

from ast.globel.globalparallel import (
    traverse_parallel as globalparallel_traverse_parallel,
    get_block_children as globalparallel_get_block_children
)

from ast.local.localnode import LocalNode as LocalNode


class LocalParallel(LocalNode):
    #blocks = None # List of localprotocolblock

    def __init__(self, local_role, blocks):
        super(LocalParallel, self).__init__(local_role)
        self.blocks = blocks

    def get_block_children(self):
        return self.blocks

    def pretty_print(self):
        blocks = self.get_block_children()
        text = constants.PAR_KW + '\n'
        text = text + blocks[0].pretty_print()
        for block in blocks[1:]:
            text = text + '\n' + constants.AND_KW + '\n'
            text = text + block.pretty_print()
        return text

    def context_visitor_enter(self, cv):
        context_ = cv.get_context()
        pushed = context_.push_localparallel(self)
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
        return cv.nf.localparallel(self.local_role, visited)
    
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

        cont_exitable = True
        for c in contexts:
            if not c.get_cont_exitable(): 
                cont_exitable = False
                break
        context_ = context_.set_cont_exitable(cont_exitable)
    
        do_exitable = True
        for c in contexts:
            if not c.get_do_exitable(): 
                do_exitable = False
                break
        context_ = context_.set_do_exitable(do_exitable)

        popped = context_.pop_localparallel(self)
        cv.set_context(popped)

    def visit(self, visitor):
        blocks = self.get_block_children()
        visited = []
        for block in blocks:
            visited.append(visitor.visit(block)) 
        return visitor.nf.localparallel(self.local_role, visited)


def traverse(traverser, node):
    return globalparallel_traverse_parallel(traverser, node,
                                            get_block_children(node))


def get_block_children(node):
    #return node.getChildren()
    return globalparallel_get_block_children(node)
