import scrib_constants as constants
import scrib_util as util


# Mostly the basic tree-based routines, Context trees mirror the AST (more
# specifically, Context tree mirrors the AST traversal pattern)
#
# Intended to be used "immutably" -- but not enforced
class AbstractContext(object):
    def __init__(self, parent=None, ast=None):
        super(AbstractContext, self).__init__()
        self.parent = parent  # AbstractContext  # The parent Context
        self.ast = ast  # CommonTree       # The corresponding AST node

    # not really a stack push, more like a linked list append
    #
    # Initial top-level context (made by Main) has no parent/ast; entering root
    # module node initialises the values
    def push(self, node_):
        c = self.clone()
        c.parent = self
        c.ast = node_
        return c

    def pop(self):
        clone = self.clone()
        # clone is replacing its parent, so clone's parent should now be the
        # parent of its parent
        clone.parent = self.parent.parent 
        # clone's AST node should now be the parent's node -- if we don't set
        # the parent, getnode will instead be a reference to the "last visited"
        # node (according to the AST traversal trace)
        clone.ast = self.parent.ast
        return clone
