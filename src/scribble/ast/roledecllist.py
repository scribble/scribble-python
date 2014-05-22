import scrib_util as util

from ast.node import Node as Node

from ast.roledecl import (
    get_declaration_name as roledecl_get_declaration_name,
    get_role_name as roledecl_get_role_name,
    get_alias_name as roledecl_get_alias_name,
    pretty_print as roledecl_pretty_print
)

from ast.globel.globalchoice import \
    DUMMY_ENABLING_OP as globalchoice_DUMMY_ENABLING_OP


class RoleDeclList(Node):
    #roledecls = None  # [ roledecl ]

    def __init__(self, roledecls):
        super(RoleDeclList, self).__init__()
        self.roledecls = roledecls
    
    # Declared names (not aliases)
    def get_role_names(self):
        roles = []
        for rd in self.roledecls:
            roles.append(rd.name)
        return roles

    def pretty_print(self):
        text = '(' + self.roledecls[0].pretty_print()
        for rd in self.roledecls[1:]:
            text = text + ', '
            text = text + rd.pretty_print()
        text = text + ')'
        return text


def traverse(traverser, node_):
    return node_


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    for rd in get_roledecl_children(node_):
        role_ = roledecl_get_declaration_name(rd)
        # Section 4.6.1 -- bound occurrences of role_ declaration names
        context_ = context_.add_role(role_)
        if context_.is_role_enabled(role_):
            raise Exception("Shouldn't get in here: ", role_)
        # Section 4.6.6 -- role_ receives before sends implemented as role_
        # enabled/disabled, here setting each declared role_ as initially enabled
        context_ = context_.enable_role(role_, globalchoice_DUMMY_ENABLING_OP)
    cv.set_context(context_)  # No push/enter


def context_visitor_visit(cv, node_):
    return node_
    
    
def context_visitor_leave(cv, node_):
    #cv.leave(node_)  # No push/enter, so no pop/leave
    pass
    

def check_wellformedness_enter(checker, node_):
    context_ = checker.get_context()
    roles = []
    for rd in get_roledecl_children(node_):
        role = roledecl_get_declaration_name(rd)
        # Section 4.6 -- Global protocol header: distinct role declaration names
        if role in roles:
            util.report_error("Bad role declaration name: " + role)
        roles.append(role)


def check_wellformedness_visit(checker, node_):
    return node_


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    rds = []
    for rd in get_roledecl_children(node_):
        rds.append(projector.visit(rd))
    new = projector.nf.roledecllist(rds)
    return new


def get_role_names(node_):
    # Not aliases (for projection and role instantiation)
    roles = []
    for rd in get_roledecl_children(node_):
        roles.append(roledecl_get_role_name(rd))
    return roles

def get_declaration_names(node_):
    roles = []
    for rd in get_roledecl_children(node_):
        roles.append(roledecl_get_declaration_name(rd))
    return roles

# FIXME: only record actual substitutions
def get_rolemap(node_):
    rolemap = {}
    for rd in get_roledecl_children(node_):
        alias = roledecl_get_alias_name(rd)
        name = roledecl_get_role_name(rd)
        if alias:
            rolemap[alias] = name
            #rolemap[name] = alias
        else:
            rolemap[name] = name
    return rolemap


# TODO: factor out with the above object method
def pretty_print(node_):
    rds = get_roledecl_children(node_)
    text = '(' + roledecl_pretty_print(rds[0]) 
    for rd in rds[1:]:
        text = text + ', '
        text = text + roledecl_pretty_print(rd)
    text = text + ')'
    return text

"""def pretty_printAux(...):
    text = '('
    first = True
    for rd in ...:
        if not(first):
            text = text + ', '
        text = text + ...
        first = False
    text = text + ')'
    return text"""


def get_roledecl_children(node_):
    return node_.getChildren()
