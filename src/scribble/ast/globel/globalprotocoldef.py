import scrib_constants as constants
import scrib_util as util


from ast.globel.globalprotocolblock import \
    pretty_print as globalprotocolblock_pretty_print

from ast.globel.globalprotocoldecl import (
    get_full_name as globalprotocoldecl_get_full_name,
    get_roledecllist_child as globalprotocoldecl_get_roledecllist_child,
    get_parameterdecllist_child as globalprotocoldecl_get_parameterdecllist_child
)

from ast.roledecllist import get_role_names as roledecllist_get_role_names

from ast.parameterdecllist import \
    get_parameter_names as parameterdecllist_get_parameter_names


ROOT_SCOPE = '0_ROOT_SCOPE'  # Identifier literals cannot start with a digit


BLOCK_INDEX = 0


def traverse(traverser, node_):
    body = get_block_child(node_)
    traversed = [traverser.traverse(body)]
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    pushed = context_.push_globalprotocoldef(node_)
    # All roles have been initially enabled with empty op in roledecllist
    cv.set_context(pushed)
    
    
def context_visitor_visit(cv, node_):
    context_ = cv.get_context()
    body = get_block_child(node_)
    visited = [cv.visit(body)]
    """unfolded = util.unfold_once(context_, body)  # FIXME: rec block collection in unfolder
    visited = [cv.visit(unfolded)]"""
    return util.antlr_dupnode_and_replace_children(node_, visited)
    
    
def context_visitor_leave(cv, node_):
    context = cv.get_context()
    context = context.pop_globalprotocoldef(node_)
    cv.set_context(context)


def check_wellformedness_enter(checker, node_):
    pass


def check_wellformedness_visit(checker, node_):
    # Section 4.6.2 -- well-formed block
    visited = context_visitor_visit(checker, node_)
    """involved = checker.rc.collect_roles(get_block_child(visited))
    # Requiring roles to be used makes various do-properties easier to check?
    # E.g. throw projection for do inside an interruptible?
    for role in get_declared_roles(visited):
        if role not in involved:
            util.report_error("Unused role declaration: " + role)"""
    return visited


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    roles = get_declared_roles(node_)
    params = get_declared_parameters(node_)
    block = projector.visit(get_block_child(node_))
    local = projector.nf.localprotocoldef(#projector.rolemap[projector.role],
                                          roles, params, projector.role, block)
    return local


def get_block_child(node_):
    return node_.getChild(BLOCK_INDEX)


def get_full_name(node_):
    #fullname = parentContext.get_current_module() + '.' + name
    fullname = globalprotocoldecl_get_full_name(node_.getParent())
    return fullname

#FIXME: naming -- declared names are not the declaration names, confusing
def get_declared_roles(node_):
    roledecllist_ = globalprotocoldecl_get_roledecllist_child(
                        node_.getParent())
    return roledecllist_get_role_names(roledecllist_)

#FIXME: naming -- declared names are not the declaration names, confusing
def get_declared_parameters(node_):
    paramdecllist_ = globalprotocoldecl_get_parameterdecllist_child(
                         node_.getParent())
    return parameterdecllist_get_parameter_names(paramdecllist_)


def pretty_print(node_):
    return globalprotocolblock_pretty_print(get_block_child(node_))
