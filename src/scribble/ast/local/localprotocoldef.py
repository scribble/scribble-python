import scrib_constants as constants
import scrib_util as util

from ast.local.localnode import LocalNode as LocalNode

from ast.local.localprotocolblock import \
    pretty_print as localprotocolblock_pretty_print


BLOCK_INDEX = 0


class LocalProtocolDef(LocalNode):
    #roles = None   # List of String
    #params = None  # List of String
    #body = None    # localprotocolblock

    # roles is independent of (so includes) local_role
    def __init__(self, roles, params, local_role, body):
    #def __init__(self, local_role, body):
        super(LocalProtocolDef, self).__init__(local_role)
        self._roles = roles
        self._params = params
        self.body = body

    def get_block(self):
        return self.body

    def pretty_print(self):
        text = self.get_block().pretty_print()
        text = text + '\n'
        return text

    def context_visitor_enter(self, cv):
        context = cv.get_context()
        pushed = context.push_localprotocoldef(self) # FIXME: local
        cv.set_context(pushed)
        
    def context_visitor_visit(self, cv):
        return self.visit(cv)
        
    def context_visitor_leave(self, cv):
        context_ = cv.get_context()
        context_ = context_.pop_localprotocoldef(self)
        cv.set_context(context_)
        
    # Currently needs context -- may add parent pointer to LocalNode later
    def get_full_name(self, context_):
        #context_.ast points to the parent LocalProtocolDecl
        name = context_.ast.get_name()  # Already has role suffix
        return context_.module + '_' + name + '.' + name

    def visit(self, visitor):
        body = self.get_block()
        visited = visitor.visit(body)
        return visitor.nf.localprotocoldef(self._roles, self._params, self.local_role,
                                           visited)

    def get_declared_roles(self):
        return self._roles

    def get_declared_parameters(self):
        return self._params


def traverse(traverser, node_):
    body = get_block_child(node_)
    traversed = [traverser.traverse(body)]
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def pretty_print(node_):
    return localprotocolblock_pretty_print(get_block_child(node_))


def get_block_child(node_):
    return node_.getChild(BLOCK_INDEX)
