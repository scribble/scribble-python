import scrib_util as util

from ast.node import Node as Node

from ast.roledecl import (
    get_role_name as roledecl_get_role_name,
    get_declaration_name as roledecl_get_declaration_name
)

from ast.roledecllist import \
    get_roledecl_children as roledecllist_get_roledecl_children

from ast.roleinstantiation import (
    get_arg as roleinstantiation_get_arg,
    has_parameter_child as roleinstantiation_has_parameter_child,
    get_parameter as roleinstantiation_get_parameter,
    pretty_print as roleinstantiation_pretty_print
)

from ast.globel.globalprotocoldecl import \
    get_roledecllist_child as \
    globalprotocoldecl_get_roledecllist_child


class RoleInstantiationList(Node):
    roleinstantiations = None  # [ roleinstantiation ]

    def __init__(self, roleinstantiations):
        super(RoleInstantiationList, self).__init__()
        self.roleinstantiations = roleinstantiations


def traverse(traverser, node_):
    traversed = []
    for child in get_roleinstantiation_children(node_):
        traversed.append(traverser.traverse(child))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


# Section 4.6.3 -- well-formed role-instantiation-list
#
# Not in the Visitor pattern directly: roleinstantiationlist used by both
# globaldo and GlobalInstantiation (i.e. different parents), more convenient to
# factor out in this way -- also, no traverse
#
# Returns rolemap to apply substitutions and visit target
def check_wellformedness(context_, target, node_):
    ris = get_roleinstantiation_children(node_)

    tree = context_.get_visible_global(target)
    rparamlist = roledecllist_get_roledecl_children(
                     globalprotocoldecl_get_roledecllist_child(tree))

    # Section 4.6.3 -- lengts of role-instantiation-list and target
    # role-decl-list are the same
    if len(ris) != len(rparamlist):
        util.report_error("Bad number of role arguments, expected: " + \
                          str(len(rparamlist)))

    croles = context_.get_roles()
    rparams = rparamlist.__iter__()
    rolemap = {}  # params -> args (as strings --
                  # maybe should do ROLE node_, as for argmap)
    for ri in ris:
        ours = roleinstantiation_get_arg(ri)
        next = rparams.next()
        theirs = roledecl_get_role_name(next)
        # Section 4.6.3 -- every role argument is bound and distinct
        if (ours not in croles) or ours in rolemap.values():
            util.report_error("Bad role argument: " + ours)
        if roleinstantiation_has_parameter_child(ri):
            tmp = roleinstantiation_get_parameter(ri)
            if theirs != tmp: 
                # Section 4.6.3 -- every instantiation parameter corresponds to
                # the declared parameter in the protocol declaration
                util.report_error("Bad role parameter: " + theirs + ", " +tmp)
        rolemap[roledecl_get_declaration_name(next)] = ours

    return rolemap


# "Type" not uniform with argumentlist.get_arg_map
def get_role_map(context_, target, node_):
    rolemap = {}  # params -> args (string -> string)
    tree = context_.get_visible_global(target)
    rparamlist = roledecllist_get_roledecl_children(
                     globalprotocoldecl_get_roledecllist_child(tree))
    rparams = rparamlist.__iter__()
    ris = get_roleinstantiation_children(node_)
    for ri in ris:
        ours = roleinstantiation_get_arg(ri)  # returns string
        next = rparams.next()
        rolemap[roledecl_get_declaration_name(next)] = ours
    return rolemap


def get_role_arguments(node_):
    ris = get_roleinstantiation_children(node_)
    roles = []
    for ri in ris:
        roles.append(roleinstantiation_get_arg(ri))
    return roles


# Could factor out these "list" printing functions
def pretty_print(node_):
    ris = get_roleinstantiation_children(node_)
    text = '(' + roleinstantiation_pretty_print(ris[0])
    for ri in ris[1:]:
        text = text + ', '
        text = text + roleinstantiation_pretty_print(ri)
    text = text + ')'
    return text


def get_roleinstantiation_children(node_): 
    return node_.getChildren()
