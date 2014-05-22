import scrib_constants as constants

from ast.local.localnode import LocalNode as LocalNode

from ast.roledecl import get_role_name as roledecl_get_role_name

from ast.roledecllist import \
    get_roledecl_children as roledecllist_get_roledecl_children

from ast.globel.globalprotocoldecl import (
    get_roledecllist_child as globalprotocoldecl_get_roledecllist_child
)

from ast.globel.globaldo import (
    traverse_do as globaldo_traverse_do,
    get_scope_child as globaldo_get_scope_child,
    get_argumentlist_child as globaldo_get_argumentlist_child,
    get_roleinstantiationlist_child as \
        globaldo_get_roleinstantiationlist_child,
    get_target_name_children as globaldo_get_target_name_children,
    get_full_name_from_visible_name as \
        globaldo_get_full_name_from_visible_name,
    EMPTY_SCOPE_NAME as globaldo_EMPTY_SCOPE_NAME
)


class LocalDo(LocalNode):
    #scope = None    # string
    #target = None   # string
    #args = None     # List of (arg, param) : (string, string)
    #roles = None    # List of (arg, param) : (string, string) 

    def __init__(self, local_role, scope, target, args, roles):
        super(LocalDo, self).__init__(local_role)
        self.scope = scope
        self.target = target
        self.args = args
        self.roles = roles
        
    def has_scope(self):
        return self.scope != globaldo_EMPTY_SCOPE_NAME

    def get_scope(self):
        return self.scope

    def get_target(self):
        return self.target

    def get_args(self):
        return self.args

    def get_roleinstantiations(self):
        return self.roles
    
    def get_role_args(self):
        roles = []
        for (arg, param) in self.roles:
            roles.append(arg)
        return roles

    def get_param_args(self):
        params = []
        for (arg, param) in self.args:
            params.append(arg)
        return params

    def pretty_print(self):
        text = constants.DO_KW + ' '
        if self.has_scope():
           text = text +  self.get_scope() + ': '
        text = text + self.get_target()
        args = self.get_args()
        if args:
            text = text + '<'
            text = text + self._pretty_print_roleinstantiation(args[0])
            for arg in args[1:]:
                text = text + ', '
                text = text + self._pretty_print_roleinstantiation(arg)
            text = text + '>'
        ris = self.get_roleinstantiations()
        text = text + '('
        text = text + self._pretty_print_roleinstantiation(ris[0])
        for ri in ris[1:]:
            text = text + ', '
            text = text + self._pretty_print_roleinstantiation(ri)
        text = text + ')'
        text = text + ';'
        return text

    # Also used for printing arguments
    def _pretty_print_roleinstantiation(self, ri):
        (a, p) = ri
        text = a
        if p:
            text = text + ' as ' + p
        return text

    def context_visitor_enter(self, cv):
        context_ = cv.get_context()
        clone = context_.clone()
        scope = self.get_scope()
        if scope != globaldo_EMPTY_SCOPE_NAME:
            clone = context_.add_scope(scope)
        do_stack = clone.peek_do_chain()
        target = self.get_target()
        if target in do_stack.keys():
            clone = clone.set_do_exitable(False)
        cv.set_context(clone)
    
    def context_visitor_visit(self, cv):
        context_ = cv.get_context()
        lpd = context_.get_projection(self.target)
        if self.get_target() not in context_.peek_do_chain().keys():
            clone = context_.push_localdo(self)
            block = lpd.get_body().get_block()
       
            # FIXME: role and arg substitution (although not needed for
            # reachability check?)
       
            cv.set_context(clone)
            cv.visit(block)
            new_context = cv.get_context()
            new_context = new_context.pop_localdo(self)
            cv.set_context(new_context)
        return self
    
    def context_visitor_leave(self, cv):
        pass

    def get_target_full_name(self, context_):
        #target = self.get_target()
        #return globaldo_get_full_name_from_visible_name(context_, target)
        return self.get_target()  # FIXME: for non qualified references

    # Duplicated from globaldo
    def get_target_parameter(self, context_):
        gpd = context_.get_visible_global(self.get_target())
        ri_list = self.get_roleinstantiations()
        rolearg = self.local_role
        rd_list = globalprotocoldecl_get_roledecllist_child(gpd)
        roleparam = None
        rd_iter = roledecllist_get_roledecl_children(rd_list).__iter__()
        for (a, p) in ri_list:
            rd = rd_iter.next()
            if a == rolearg:
                if p:
                    roleparam = p
                else:
                    roleparam = roledecl_get_role_name(rd)
                    # actually, this else case subsumes the first case
                break
        return roleparam

    def collect_subprotocols(self, collector):
        collector.add_subprotocol(self.get_target())
        return self  # could do super call


def traverse(traverser, node_):
    return globaldo_traverse_do(traverser, node_, get_scope_child(node_),
                                get_argumentlist_child(node_),
                                get_roleinstantiationlist_child(node_),
                                get_target_name_children(node_))


def get_scope_child(node_):
    return globaldo_get_scope_child(node_)

def get_argumentlist_child(node_):
    return globaldo_get_argumentlist_child(node_)

def get_roleinstantiationlist_child(node_):
    return globaldo_get_roleinstantiationlist_child(node_)

def get_target_name_children(node_):
    return globaldo_get_target_name_children(node_)
