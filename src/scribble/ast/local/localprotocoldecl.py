import scrib_constants as constants
import scrib_util as util

from ast.roledecllist import (
    get_role_names as roledecllist_get_role_names,
    pretty_print as roledecllist_pretty_print
)

from ast.parameterdecllist import (
    EMPTY_PARAMETER_DECL_LIST as parameterdecllist_EMPTY_PARAMETER_DECL_LIST,
    pretty_print as parameterdecllist_pretty_print
)

from ast.role import get_role_name as role_get_role_name

from ast.local.localnode import LocalNode as LocalNode

from ast.local.localprotocoldef import (
    LocalProtocolDef as LocalProtocolDef,
    pretty_print as localprotocoldef_pretty_print
)


##
# Not currently checking well-formedness on local protocols
#


PROTOCOL_NAME_INDEX = 0
LOCAL_ROLE_NAME_INDEX = 1
PARAMETER_DECL_LIST_INDEX = 2
ROLE_DECL_LIST_INDEX = 3
BODY_INDEX = 4  # LOCALPROTOCOLDEF or LOCALPROTOCOLINSTANCE


class LocalProtocolDecl(LocalNode):
    #name = None     # String
    #role_ = None  # String
    #paramdecllist_ = None  # parameterdecllist
    #roledecllist_ = None  # roledecllist_
    #body = None    # localprotocoldef or Instance

    def __init__(self, local_role, name, paramdecllist_, roledecllist_, body):
        super(LocalProtocolDecl, self).__init__(local_role)
        self.name = name
        self.paramdecllist_ = paramdecllist_
        self.roledecllist_ = roledecllist_
        self.body = body

    # Includes local role suffix
    def get_name(self):
        return self.name

    # Should be deprecated
    def get_local_role(self):
        return self.local_role

    def get_parameterdecllist(self):
        return self.paramdecllist_
    
    def has_parameterdecllist(self):
        return self.paramdecllist_ is not None

    def get_roledecllist(self):
        return self.roledecllist_
    
    def get_role_names(self):
        return self.roledecllist_.get_role_names()

    def get_parameter_names(self):
        if self.has_parameterdecllist():
            return self.paramdecllist_.get_parameter_names()
        return []

    def get_body(self):
        return self.body

    def pretty_print(self):
        text = ""
        text = text + constants.LOCAL_KW + ' ' + constants.PROTOCOL_KW + ' '
        text = text + self.get_name() + ' '
        text = text + constants.AT_KW + ' ' + \
            self.get_local_role()
        if self.paramdecllist_ is not None:
            text = text + self.paramdecllist_.pretty_print()
        text = text + self.roledecllist_.pretty_print() + ' '
        child = self.get_body()
        if type(child) == LocalProtocolDef:
            text = text + child.pretty_print()
        else:
            raise RuntimeError("TODO:", type(child))
        return text

    def context_visitor_enter(self, cv):
        pushed = cv.get_context().push_globalprotocoldecl(self)  # FIXME: local
        cv.set_context(pushed)

    def context_visitor_visit(self, cv):
        return self.visit(cv)
    
    def context_visitor_leave(self, cv):
        popped = cv.get_context().pop_globalprotocoldecl(self)
        cv.set_context(popped)
        
    def get_full_name(self, context_):
        proto = self.get_name()
        return get_full_name(context_.module, proto, proto)
    
    def visit(self, visitor):
        name = self.get_name()
        role_ = self.get_local_role()
        paramdecllist_ = self.get_parameterdecllist()
        roledecllist_ = self.get_roledecllist()
        body = self.get_body()
        visited = visitor.visit(body)
        return visitor.nf.localprotocoldecl(role_, name, paramdecllist_,
                                            roledecllist_, visited)
    

def traverse(traverser, node_):  # Duplicated from check_wellformedness_visit
    name = get_name_child(node_)
    role = get_local_role_child(node_)
    roledecllist = get_roledecllist_child(node_)
    pds = get_parameterdecllist_child(node_)
    body = get_child(node_)

    traversed = []
    traversed.append(name)  # No need to traverse
    traversed.append(role)  # No need to traverse
    if util.get_node_type(pds) == parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        traversed.append(pds)
    else:
        traversed.append(traverser.traverse(pds))
    traversed.append(traverser.traverse(roledecllist))
    traversed.append(traverser.traverse(body))
    return util.antlr_dupnode_and_replace_children(node_, traversed) 



def get_name(node_):
    return get_name_child(node_).getText()

def get_local_role_name(node_):
    return role_get_role_name(get_local_role_child(node_))

def get_roles(node_):
    return roledecllist.get_role_names(get_roledecllist_child(node_))

def get_full_name(module_name, local_proto_name):
    return module_name + '_' + local_proto_name + '.' + local_proto_name


def pretty_print(node_):
    return _pretty_print_aux(get_name(node_),
                           get_local_role_child(node_),
                           get_parameterdecllist_child(node_),
                           get_roledecllist_child(node_),
                           get_child(node_))

# FIXME: integrate with object method (careful about node_ types)
def _pretty_print_aux(p, r, paramdecllist_, roledecllist_, body):
    text = ""
    text = text + constants.LOCAL_KW + ' ' + constants.PROTOCOL_KW + ' '
    text = text + p + ' '
    text = text + constants.AT_KW + ' ' + role_get_role_name(r)
    if util.get_node_type(paramdecllist_) != \
            parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        text = text + parameterdecllist_pretty_print(paramdecllist_)
    text = text + roledecllist_pretty_print(roledecllist_)
    child = body
    if util.get_node_type(child) == constants.LOCAL_PROTOCOL_DEF_NODE_TYPE:
        text = text + localprotocoldef_pretty_print(child)
    else:
        raise RuntimeError("TODO:", util.get_node_type(child))
    return text


def get_name_child(node_):
    return node_.getChild(PROTOCOL_NAME_INDEX)
def get_local_role_child(node_):
    return node_.getChild(LOCAL_ROLE_NAME_INDEX)

def get_roledecllist_child(node_):
    return node_.getChild(ROLE_DECL_LIST_INDEX)

def get_parameterdecllist_child(node_):
    return node_.getChild(PARAMETER_DECL_LIST_INDEX)

def get_child(node_):  # def or instance
    return node_.getChild(BODY_INDEX)
