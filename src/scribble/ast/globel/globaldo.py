import scrib_constants as constants
import scrib_util as util

from visibilitybuilder import build_visibility as build_visibility
from namesubstitutor import NameSubstitutor

from ast.argumentlist import (
    is_empty as argumentlist_is_empty,
    check_wellformedness as argumentlist_check_wellformedness,
    #get_argument_children as argumentlist_get_argument_children,
    get_argument_children as argumentlist_get_children,
    pretty_print as argumentlist_pretty_print,
    get_argument_args as argumentlist_get_args
)

from ast.module import get_moduledecl_child as module_get_moduledecl_child
from ast.moduledecl import get_full_name as moduledecl_get_full_name
from ast.roledecl import get_role_name as roledecl_get_role_name
from ast.roledecllist import \
    get_roledecl_children as roledecllist_get_roledecl_children

from ast.roleinstantiation import (
    get_arg as roleinstantiation_get_arg,
    get_parameter as roleinstantiation_get_parameter,
    get_parameter_child as roleinstantiation_get_parameter_child,
    pretty_print as roleinstantiation_pretty_print
)

from ast.argument import (
    get_arg as argument_get_arg,
    get_parameter as argument_get_parameter
    #get_parameter_child as roleinstantiation_get_parameter_child,
    #pretty_print as roleinstantiation_pretty_print
)

from ast.roleinstantiationlist import (
    check_wellformedness as roleinstantiationlist_check_wellformedness,
    get_roleinstantiation_children as \
        roleinstantiationlist_get_children,
    pretty_print as roleinstantiationlist_pretty_print,
    get_role_arguments as roleinstantiationlist_get_roles
)

from ast.globel.globalprotocoldecl import (
    get_name as globalprotocoldecl_get_name,
    get_child as globalprotocoldecl_get_child,
    get_roledecllist_child as \
        globalprotocoldecl_get_roledecllist_child
)

from ast.globel.globalprotocoldef import \
    get_block_child as globalprotocoldef_get_block_child


EMPTY_SCOPE_NAME = 'EMPTY_SCOPE_NAME'


# A fake recursion label to make Context.has_exit false
#NON_CONTINUABLE_HACK = '__NON_CONTINUABLE_HACK' 

SCOPE_NAME_INDEX = 0
ARGUMENT_LIST_INDEX = 1
ROLE_INSTANTIATION_LIST_INDEX = 2
TARGET_NAME_START_INDEX = 3


def traverse_do(traverser, node_, scope, arglist, rolelist, target):
    traversed = []
    traversed.append(traverser.traverse_untyped_leaf(scope))
    if argumentlist_is_empty(arglist):
        traversed.append(arglist)
    else:
        traversed.append(traverser.traverse(arglist))
    traversed.append(traverser.traverse(rolelist))
    for t in target:
        traversed.append(traverser.traverse_untyped_leaf(t))
    return util.antlr_dupnode_and_replace_children(node_, traversed)

def traverse(traverser, node_):
    return traverse_do(traverser, node_, get_scope_child(node_),
                      get_argumentlist_child(node_),
                      get_roleinstantiationlist_child(node_),
                      get_target_name_children(node_))


def context_visitor_enter(cv, node_):
    context_ = cv.get_context()
    clone = context_.clone()
    scope = get_scope(node_)
    if scope != EMPTY_SCOPE_NAME:
        clone = context_.add_scope(scope)
    do_frame = clone.peek_do_chain()
    fullname = get_target_full_name(clone, node_)
    if fullname in do_frame.keys():
        clone = context_.set_do_exitable(False)
    # targetSubstitutor replaces the nested protocol context_ targets with outer
    # ones, so enabledroles etc. are already the correct targets
    cv.set_context(clone)


def context_visitor_visit(cv, node_):
    return node_


def context_visitor_leave(cv, node_):
    pass


def check_wellformedness_enter(checker, node_):
    
    #print "b: ", util.pretty_print(node_), context_.get_visible_globals() 
    
    context_ = checker.get_context()
    scope = get_scope(node_)
    target = get_target(node_)
        # Should be a visible protocol name, but not necessarily the full name

    # Section 4.6.2 -- distinct scope names
    if scope != EMPTY_SCOPE_NAME and scope in context_.get_current_scopes():
        util.report_error("Bad scope: " + scope)

    # Section 4.6.10 -- target protocol must be visible
    globals = context_.get_visible_globals()
    if target not in globals.keys():
        #tmp = context_.get_current_module() + '.' + target
            # All visible globals should already be collected by
            # VisibilityBuilder now
        #if not(tmp in globals.keys()):
        util.report_error("Bad protocol reference: " + target)

    # Section 4.6.2 -- Distinct scope checked above
    #
    # Checking for bad recursive-do from within parallel (FIXME: not currently
    # specified in langref)
    #
    # No way for a recursive-do to be good inside a parallel, unless it's a
    # singleton parallel, but ignoring that special case for now
    do_frame = context_.peek_do_chain()
    fullname = get_target_full_name(context_, node_)
    if fullname in do_frame.keys():
        # Recursive-do to this protocol has been forbidden by entering a
        # parallel context_
        if not do_frame[fullname]:
            util.report_error("Bad do: " + fullname)
        """if scope == EMPTY_SCOPE_NAME:  # Is this needed?
            util.report_error("Bad recursive do: " + fullname)"""


# Check "contractive" recursive do's?
def check_wellformedness_visit(checker, node_):
    context_ = checker.get_context()
    visited = context_visitor_visit(checker, node_)
    scope = get_scope(visited)
    target = get_target(visited)
    argmap = None # Map from parameter name (String) to argument
                  # (messagesignature node_)

    rolemap = None # Map from role parameter name (String) to role argument name
                   # (String) not uniform with argmap

    # Section 4.6.10 -- Well-formed argument-list
    arglist = get_argumentlist_child(visited)
    argmap = argumentlist_check_wellformedness(checker, target, arglist)

    # Section 4.6.10 -- Well-formed role-decl-list
    #roleinstantiations = roleinstantiationlist.get_roleinstantiation_children(get_roleinstantiationlist_child(node_))
    roleinstantiations = get_roleinstantiationlist_child(visited)
    rolemap = roleinstantiationlist_check_wellformedness(context_,
                                                         target,
                                                         roleinstantiations)

    ##
    # Section 4.6.10 -- "well-formedness conditions imposed by context_ myust be
    # respected by the target protocol definition" -- currently not specified
    # very precisely in langref
    #
    # Scope prefix is applied to operators (globalmessagetransfer) and recursion
    # labels (Context, globalrecursion, globalcontinue)  -- and others?
    #
    # However, substitution and visit are still needed for checking e.g. choice
    # branch role mergability
    gpd = context_.get_visible_global(target)
    module_ = gpd.getParent()
    modulefullname = moduledecl_get_full_name(module_get_moduledecl_child(module_))
    protofullname = modulefullname + '.' + \
            globalprotocoldecl_get_name(gpd)
        # Same as in get_target_full_name, but we also need the above bits
        # later as well as the name

    #do_frame = context_.peek_do_chain()
    
    roles = get_argument_roles(node_)
    args = get_argument_args(node_)
    #if protofullname not in do_frame.keys():  # Factor out

    new_context = context_
    if not context_.do_instance_in_chain(protofullname, roles, args):
    #{
        clone = context_.clone()
    
        # Gets fully qualified names of all visible entities
        clone = build_visibility(clone, module_) 
            # But not pure? i.e. adds on top of existing?
        # In a regular pass, set by visiting moduledecl
        clone = clone.set_current_module(modulefullname) 
        # Not being done in enter because this push is for visiting the child
        # (i.e. the do target protocol), not this do statement itself
        clone = clone.push_globaldo(visited) 

        tmp = globalprotocoldecl_get_child(gpd)
        if util.get_node_type(tmp) != constants.GLOBAL_PROTOCOL_DEF_NODE_TYPE:
            # TODO: could be GlobalProtocolInstance
            raise RuntimeError("TODO: " + util.get_node_type(tmp))
        block = globalprotocoldef_get_block_child(tmp)

        substitutor = NameSubstitutor(rolemap, argmap)
        substituted = substitutor.substituteNames(block)

        checker.set_context(clone)
            # is it better to just make a new WellformednessChecker?
        checker.check_wellformedness(substituted)  # discarding the return

        new_context = checker.get_context()
        new_context = new_context.pop_globaldo(visited)
    #}
    checker.set_context(new_context)
    return visited


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    context_ = projector.context
    rolearg = projector.role
    scope = get_scope(node_)
    target = get_target_full_name(context_, node_)
    gpd = context_.get_visible_global(target)
    #fullname = globalprotocoldecl.get_full_name(gpd)

    rd_list = globalprotocoldecl_get_roledecllist_child(gpd)
    ri_list = get_roleinstantiationlist_child(node_)
    roleparam = get_target_parameter(rd_list, ri_list, rolearg)

    if roleparam is None:
        return None
    else:
    #{
        roles = []
        rd_iter = roledecllist_get_roledecl_children(rd_list).__iter__()
        for ri in roleinstantiationlist_get_children(ri_list):
            rd = rd_iter.next()
            #roles.append(roleinstantiation_pretty_print(ri))  # FIXME: string hack (localdo)
            #tmp = projector.rolemap[roleinstantiation_get_arg(ri)]
            tmp = roleinstantiation_get_arg(ri)
            roles.append((tmp, roleinstantiation_get_parameter(ri)))

        args = []
        #pd_list = globalprotocoldecl_get_parameterdecllist_child(gpd)
        arglist = get_argumentlist_child(node_)
        ##for arg in argumentlist_get_argument_children(arglist):
        ##    args.append(argument_pretty_print(arg))
        #pd_iter = parameterdecllist_get_paramdecl_children(pd_list).__iter__()
        for arg in argumentlist_get_children(arglist):
            #pd = rd_iter.next()
            tmp = argument_get_arg(arg)
            args.append((tmp, argument_get_parameter(arg)))

        """members = context_.get_members()

        for arg in globaldo.getglobaldoArgsChildren(globel):
            if util.get_node_type(arg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
                for payload in payloadList.getpayloadChildren(messagesignature.getpayloadListChild(arg)):
                    alias = payload.getpayloadType(payload)
                    payloads[len(payloads)-1][alias] = context_.getpayloadTypes()[alias]

        if not((fqmn, param) in visited.keys()) or not(globalprotocoldecl.get_name(gpd) in visited[(fqmn, param)]):
            target = project(context_.get_source(fqmn), context_, fqmn, gpd, param)  # FIXME: only need to do for target parameter
        imports[len(imports)-1].add(fqmn + '_' + param)"""

        if target in context_.get_members():
            # Full member name of target was specified
            #module_ = util.get_full_module_name_from_full_member_name(target)
            #proto = util.get_simple_member_name_from_full_member_name(target)
            projectionname = get_projected_member_name(target, roleparam)
                # FIXME: factor out local projection name generation with import
                # decl projection
            #projector.add_subprotocol_reference(target, roleparam)
        else:
            # TODO: several cases, could be via simple name of co-module_
            # protocol, or full name via member alias or module_ alias, etc.
            #
            # One option is to project all references to be fully qualified
            # (dropping aliases even?)
            raise RuntimeError("[Projector] globaldo TODO: " + target)

        return projector.nf.localdo(#projector.rolemap[projector.role],
                                    projector.role,
                                    scope,
                                    projectionname,
                                    args,
                                    roles)
    #}


def has_empty_argumentlist(node_):
    return argumentlist_is_empty(get_argumentlist_child(node_));

def get_scope(node_):
    return get_scope_child(node_).getText()

# The explicitly specified target, which should be a visible protocol
def get_target(node_):
    # Make a MemberName category? (uniform with e.g. role and parameter)
    #return get_targetChild(node_).getText()
    names = get_target_name_children(node_)
    return util.parse_dot_separated_name_from_node_list(names)

def get_target_full_name(context_, node_):
    target = get_target(node_)
    return get_full_name_from_visible_name(context_, target)

def get_target_parameter(rd_list, ri_list, rolearg):
    roleparam = None
    rd_iter = roledecllist_get_roledecl_children(rd_list).__iter__()
    for ri in roleinstantiationlist_get_children(ri_list):
        rd = rd_iter.next()
        if roleinstantiation_get_arg(ri) == rolearg:
            if roleinstantiation_get_parameter_child(ri):
                roleparam = roleinstantiation_get_parameter(ri)
            else:
                roleparam = roledecl_get_role_name(rd)
                # actually, this else case subsumes the first case
            break
    return roleparam

def get_argument_roles(node_):
    ril = get_roleinstantiationlist_child(node_)
    return roleinstantiationlist_get_roles(ril)

def get_argument_args(node_):
    al = get_argumentlist_child(node_)
    return argumentlist_get_args(al)
        

# Move to a more suitable module
def get_full_name_from_visible_name(context_, globalproto):
    gpd = context_.get_visible_global(globalproto)
    if gpd is None:  # Should never happen?
        util.report_error("Bad protocol reference: " + target)
    module_ = gpd.getParent()
    modulefullname = moduledecl_get_full_name(
                         module_get_moduledecl_child(module_))
    protofullname = modulefullname + '.' + globalprotocoldecl_get_name(gpd)
    return protofullname

def get_projected_member_name(full_global_member_name, role_):
    module_ = util.get_full_module_name_from_full_member_name(
                  full_global_member_name)
    proto = util.get_simple_member_name_from_full_member_name(
                  full_global_member_name)
    return module_ + '_' + proto + '_' + role_ + '.' + proto + '_' + role_


def pretty_print(node_):
    text = constants.DO_KW + ' '
    text = text + get_scope(node_) + ': '
    text = text + get_target(node_)
    text = text + argumentlist_pretty_print(get_argumentlist_child(node_))
    ril = get_roleinstantiationlist_child(node_)
    text = text + roleinstantiationlist_pretty_print(ril)
    text = text + ';'
    return text


def get_scope_child(node_):
    return node_.getChild(SCOPE_NAME_INDEX)

def get_argumentlist_child(node_):
    return node_.getChild(ARGUMENT_LIST_INDEX)

def get_roleinstantiationlist_child(node_):
    return node_.getChild(ROLE_INSTANTIATION_LIST_INDEX)

def get_target_name_children(node_):
    return node_.getChildren()[TARGET_NAME_START_INDEX:]
