from ast.node import Node as Node

from ast.role import get_role_name as role_get_name


NAME_INDEX = 0
ALIAS_INDEX = 1


class RoleDecl(Node):
    #name = None  # string
    #alias = None  # string

    def __init__(self, name, alias):
        super(RoleDecl, self).__init__()
        self.name = name
        self.alias = alias

    def pretty_print(self):
        # self.alias is None for no alias
        return _pretty_print_aux(self.name, self.alias) 

    def has_alias(self):
        return self.alias is not None


def project(projector, node_):
    name = get_role_name(node_)
    alias = None
    if has_alias(node_):
        alias = get_alias_name(node_)
    return projector.nf.roledecl(name, alias)
    #return projector.nf.roledecl(name, None)


def has_alias(node_):
    return node_.getChildCount() > 1  # Factor out constant?

def get_role_name(node_):
    return role_get_name(get_role_child(node_))

def get_alias_name(node_):
    if has_alias(node_):
        return role_get_name(get_alias_child(node_))
    else:
        return None


##
# Section 4.1 -- role declaration name
def get_declaration_name(node_):
    if node_.getChildCount() > 1:
        return get_alias_name(node_)
    else:
        return get_role_name(node_)


def pretty_print(node_):
    role = get_role_name(node_)
    alias = None
    if has_alias(node_):
         alias = get_alias_name(node_)
    return _pretty_print_aux(role, alias)

def _pretty_print_aux(name, alias):
    text = 'role ' + name
    if alias is not None:
        text = text + ' as ' + alias
    return text


def get_role_child(node_):
    return node_.getChild(NAME_INDEX)

def get_alias_child(node_):
    return node_.getChild(ALIAS_INDEX)
