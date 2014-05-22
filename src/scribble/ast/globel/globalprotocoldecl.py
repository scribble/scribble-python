import scrib_constants as constants
import scrib_util as util

from ast.module import get_moduledecl_child as module_get_moduledecl_child
from ast.moduledecl import get_full_name as moduledecl_get_full_name

from ast.roledecllist import (
    get_role_names as roledecllist_get_role_names,
    get_rolemap as roledecllist_get_rolemap,
    pretty_print as roledecllist_pretty_print
)

from ast.parameterdecllist import (
    EMPTY_PARAMETER_DECL_LIST as parameterdecllist_EMPTY_PARAMETER_DECL_LIST,
    pretty_print as parameterdecllist_pretty_print,
    get_parameter_names as parameterdecllist_get_param_names
)


PROTOCOL_NAME_INDEX = 0
PARAMETER_DECL_LIST_INDEX = 1
ROLE_DECL_LIST_INDEX = 2
BODY_INDEX = 3  # GLOBALPROTOCOLDEF or GLOBALPROTOCOLINSTANCE


def traverse(traverser, node_):
    name = get_name_child(node_)
    roledecllist_ = get_roledecllist_child(node_)
    pds = get_parameterdecllist_child(node_)
    body = get_child(node_)
    traversed = []
    traversed.append(name)  # No need to traverse
    if util.get_node_type(pds) == parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        traversed.append(pds)
    else:
        traversed.append(traverser.traverse(pds))
    traversed.append(traverser.traverse(roledecllist_))
    traversed.append(traverser.traverse(body))
    # rebuild using new children
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def context_visitor_enter(cv, node_):
    pushed = cv.get_context().push_globalprotocoldecl(node_)
    cv.set_context(pushed)


def context_visitor_visit(cv, node_):
    name = get_name_child(node_)
    pds = get_parameterdecllist_child(node_)
    roledecllist_ = get_roledecllist_child(node_)
    body = get_child(node_)
        # globalprotocoldef or GlobalProtocolInstance
    visited = []
    visited.append(name)  # No need to visit
    if util.get_node_type(pds) == parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        visited.append(pds)
    else:
        visited.append(cv.visit(pds))
    visited.append(cv.visit(roledecllist_))
    visited.append(cv.visit(body))
    # rebuild using new children
    return util.antlr_dupnode_and_replace_children(node_, visited) 


def context_visitor_leave(cv, node_):
    popped = cv.get_context().pop_globalprotocoldecl(node_)
    cv.set_context(popped)
    

def check_wellformedness_enter(checker, node_):
    pass


# check declared roles are actually used in the protocol?
#
# TODO: Section 4.6 -- reachable projections (currently implemented at the
# global level via Context continuable, but specified in langref as the
# reachability property on projected local protocols)
def check_wellformedness_visit(checker, node_):
    # Section 4.6 -- Global Protocol Declarations: well-formed header (parameter
    # and role declarations) and well-formed definition or instance, handled by
    # general ContextVisitor pattern
    visited = context_visitor_visit(checker, node_)
    
    """name = get_name_child(node_)
    pds = get_parameterdecllist_child(node_)
    roledecllist_ = get_roledecllist_child(node_)
    body = get_child(node_)
        # globalprotocoldef or GlobalProtocolInstance
    visited = []
    visited.append(name)  # No need to visit
    if util.get_node_type(pds) == parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        visited.append(pds)
    else:
        visited.append(checker.visit(pds))
    visited.append(checker.visit(roledecllist_))
    checker.visit(body)  # Don't reconstruct the unfolding
    visited.append(body)
    return util.antlr_dupnode_and_replace_children(node_, visited) """
    

    """# check reachability and guarded recursions-do for each projection
    child = get_child(node_)
    if util.get_node_type(child) == constants.GLOBAL_PROTOCOL_DEF_NODE_TYPE:
        for r in roledecllist_get_role_names(get_roledecllist_child(node_)):
            context_ = checker.get_context()  # Only really need member info
            projection = checker.projector.project(context_, node_, r)
            rc = checker.create_reachability_checker(r)
            tmp = rc.check_reachability(projection)

            print "Projection reachbility checked:", r, "\n", projection.pretty_print(), "\n"
    else:
        raise RuntimeError("TODO: " + child_)"""
    
    return visited


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    rdl = get_roledecllist_child(node_)
    rolemap = roledecllist_get_rolemap(rdl) 
    role_ = rolemap[projector.role]
    if role_ not in get_role_name(node_):
        return None

    role_ = rolemap[projector.role]
    name = get_name(node_) + '_' + role_
    pdl = get_parameterdecllist_child(node_)
    paramdecllist = None
    if util.get_node_type(pdl) != parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        paramdecllist = projector.visit(pdl)
    roledecllist = projector.visit(get_roledecllist_child(node_))
    body = projector.visit(get_child(node_))
    local = projector.nf.localprotocoldecl(role_, name,
                                           paramdecllist, roledecllist, body)
    return local


def get_name(node_):
    return get_name_child(node_).getText()

# FIXME: rename to get_role_names
def get_role_name(node_):
    return roledecllist_get_role_names(get_roledecllist_child(node_))

def get_parameter_names(node_):
    return parameterdecllist_get_param_names(get_parameterdecllist_child(node_))

def get_full_name(node_):
    moduledecl_ = module_get_moduledecl_child(node_.getParent())
    fmn = moduledecl_get_full_name(moduledecl_)
    proto = get_name(node_)
    return fmn + '.' + proto


def pretty_print(node_):
    text = constants.GLOBAL_KW + ' ' + constants.PROTOCOL_KW + ' '
    text = text + get_name(node_)
    pds = get_parameterdecllist_child(node_)
    if util.get_node_type(pds) != parameterdecllist_EMPTY_PARAMETER_DECL_LIST:
        text = text + parameterdecllist_pretty_print(pds)
    text = text + roledecllist_pretty_print(get_roledecllist_child(node_))
    body = get_child(node_)
    if util.get_node_type(body) == constants.GLOBAL_PROTOCOL_DEF_NODE_TYPE:
        text = text + '\n' + util.pretty_print(body)
    else:
        raise RuntimeError("TODO: ")
    return text


##
# AST helpers

def get_name_child(node_):
    return node_.getChild(PROTOCOL_NAME_INDEX)

def get_roledecllist_child(node_):
    return node_.getChild(ROLE_DECL_LIST_INDEX)

def get_parameterdecllist_child(node_):
    return node_.getChild(PARAMETER_DECL_LIST_INDEX)

def get_child(node_):  # def or instance
    return node_.getChild(BODY_INDEX)
