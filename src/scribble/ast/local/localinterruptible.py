import scrib_constants as constants
import scrib_util as util

from ast.local.localnode import LocalNode as LocalNode

from ast.local.localprotocolblock import \
    pretty_print as localprotocolblock_pretty_print
from ast.local.localthrow import pretty_print as localthrow_pretty_print
from ast.local.localcatch import pretty_print as localcatch_pretty_print


EMPTY_LOCAL_THROW = 'EMPTY_LOCAL_THROW'


SCOPE_NAME_INDEX = 0
INTERRUPTIBLE_BLOCK_INDEX = 1
THROW_INDEX = 2
CATCH_START_INDEX = 3


class LocalInterruptible(LocalNode):
    #scope = None    # string
    #block = None    # localprotocolblock
    #throws = None   # localthrow
    #catches = None  # [ localcatch ]

    def __init__(self, local_role, scope, block, throw, catches):
        super(LocalInterruptible, self).__init__(local_role)
        self.scope = scope
        self.block = block
        self.throw = throw
        self.catches = catches
        
    def get_scope(self):
        return self.scope

    def get_block_child(self):
        return self.block
    
    def has_throw(self):
        return self.throw is not None

    def get_throw(self):
        return self.throw

    def get_catches(self):
        return self.catches

    def pretty_print(self):
        text = ""
        text = text + constants.INTERRUPTIBLE_KW + ' '
        text = text + self.get_scope() + '\n'
        text = text + self.get_block_child().pretty_print() + '\n'
        text = text + constants.WITH_KW + ' {\n'
        throws = self.get_throw()
        if self.has_throw():
            text = text + self.throw.pretty_print()
            text = text + '\n'
        catches = self.get_catches()
        if catches:
            text = text + catches[0].pretty_print() + '\n'
            for catch in catches[1:]:
                text = text + catch.pretty_print() + '\n'
        text = text + '}'
        return text

    def context_visitor_enter(self, cv):
        context = cv.get_context()
        pushed = context.push_localinterruptible(self)
        cv.set_context(pushed)
    
    def context_visitor_visit(self, cv):
        return self.visit(cv)
    
    def context_visitor_leave(self, cv):
        context_ = cv.get_context()
        if self.get_throw() or self.get_catches():
            context_ = context_.set_rec_exitable(True)
            context_ = context_.set_cont_exitable(True)
            context_ = context_.set_do_exitable(True)
        cv.set_context(context_.pop_localinterruptible(self))

    def visit(self, visitor):
        scope = self.get_scope()
        block = self.get_block_child()
        throw = self.get_throw()
        catches = self.get_catches()
        visited = visitor.visit(block)
        return visitor.nf.localinterruptible(self.local_role, scope, visited,
                                             throw, catches)


def traverse(traverser, node_):
    scope = get_scope_child(node_)
    block = get_block_child(node_)
    throw = get_throw_child(node_)
    catches = get_catch_children(node_)
    traversed = []
    traversed.append(scope)
    traversed.append(traverser.traverse(block))
    if has_throw_child(node_):
        traversed.append(traverser.traverse(throw))
    else:
        traversed.append(traverser.traverse_untyped_leaf(throw))
    for catch in catches:
        traversed.append(traverser.traverse(catch))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def get_scope(node_):
    return get_scope_child(node_).getText()


def pretty_print(node_):
    text = ""
    text = text + constants.INTERRUPTIBLE_KW
    text = text + get_scope(node_)+ '\n'
    text = text + localprotocolblock_pretty_print(get_block_child(node_)) + '\n'
    text = text + constants.WITH_KW + ' {\n'
    if has_throw_child(node_):
        text = text + localthrow_pretty_print(get_throw_child(node_))
    for c in get_catch_children(node_):
        text = text + localcatch_pretty_print(c) + '\n'
    text = text + '}'
    return text


# The throw position is not the dummy empty throw
def has_throw_child(node_):
    return node_.getChild(THROW_INDEX).getText() != EMPTY_LOCAL_THROW


def get_scope_child(node_):
    return node_.getChild(SCOPE_NAME_INDEX)

def get_block_child(node_):
    return node_.getChild(INTERRUPTIBLE_BLOCK_INDEX)

# Can be the dummy empty throw node_
def get_throw_child(node_):
    return node_.getChild(THROW_INDEX)

def get_catch_children(node_):
    return node_.getChildren()[CATCH_START_INDEX:]
