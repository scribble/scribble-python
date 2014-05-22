import scrib_constants as constants
import scrib_util as util

from ast.messagesignature import (
    get_operator as messagesignature_get_operator,
    check_wellformedness as messagesignature_check_wellformedness,
    pretty_print as messagesignature_pretty_print
)

from ast.role import get_role_name as role_get_name

from ast.parameter import (
    get_parameter_name as parameter_get_name,
    pretty_print as parameter_pretty_print
)


MESSAGE_INDEX = 0
SENDER_INDEX = 1
FIRST_RECEIVER_INDEX = 2


def traverse(traverser, node_):
    traversed = []
    msg = get_message_child(node_)
    if util.get_node_type(msg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        traversed.append(traverser.traverse(msg))
    else:
        traversed.append(traverser.traverse_untyped_leaf(msg))
    src = get_source_child(node_)
    traversed.append(traverser.traverse_untyped_leaf(src))
    for dest in get_destination_children(node_):
        traversed.append(traverser.traverse_untyped_leaf(dest))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def context_visitor_enter(cv, node_):
    clone = cv.get_context().clone()
    msg = get_message_child(node_)   # node
    mtype = util.get_node_type(msg)
    src = get_source(node_)         # string
    dests = get_destinations(node_) # string

    # Will be assigned depending on whether message is a concrete signature or a parameter
    op = None     # string
    param = None  # string
    if mtype == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        op = clone.get_current_scope() + '.' + messagesignature_get_operator(msg)
    else: # Not a message signature, should be a sig parameter
        param = parameter_get_name(msg)
        op = param

    # Destination roles
    for dest in dests:
        # Section 4.6.8 -- collecting "potential" operators, for parallel
        # well-formedness Also parameters potential (op is param for sig
        # parameters)
        #
        # Building a conservative set (potential actions, for parallel
        # well-formedness)
        clone = clone.add_operator(src, dest, op)

        #Section 4.6.6 -- destination roles are now "enabled" (if not already)
        #for action" within the (choice) block
        if not clone.is_role_enabled(dest):
            # Because clone is cloned, all previously enabled/disabled is
            # automatically carried over. but could factor out this aspect from
            # here and other categories into the sequencing constructor
            if mtype == constants.MESSAGE_SIGNATURE_NODE_TYPE:
                clone = clone.enable_role(dest, op)
            else:  # sig parameter
                clone = clone.enable_role(dest, param)

    cv.set_context(clone)


def context_visitor_visit(cv, node_):
    return node_


def context_visitor_leave(cv, node_):
    pass


# Global transfer well-formedness checking does not modify node_, but does update
# clone -- so all the work is done in this procedure
#
# Self-communication currently allowed, is this OK?
def check_wellformedness_enter(checker, node_):
    context = checker.get_context()
    msg = get_message_child(node_)   # node
    mtype = util.get_node_type(msg)
    src = get_source(node_)         # string
    dests = get_destinations(node_) # string

    # Will be assigned depending on whether message is a concrete signature or a
    # parameter
    op = None     # string
    param = None  # string

    # Section 4.6.5 -- message is a well-formed message-signature or a bound sig
    # parameter
    if mtype == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        # Section 4.6.5 -- Well-formed message-signature
        messagesignature_check_wellformedness(checker, msg)
        #op = messagesignature.get_operator(msg)
        op = context.get_current_scope() + '.' + messagesignature_get_operator(msg)
    else:
        # Not a message signature, should be a sig parameter
        param = parameter_get_name(msg)
        op = param
        params = context.get_parameters()
        if not param in params.keys():  # Bound parameter
            util.report_error("Bad parameter: " + param)
        if params[param] != constants.KIND_MESSAGE_SIGNATURE:
            # sig parameter  # HACK?: using the KW
            util.report_error("Bad type parameter: " + param)

    # Section 4.6.5 -- source role is bound
    if not context.is_role_declared(src):
        util.report_error("Bad source role: " + src)
    # Section 4.6.6 -- the non-at roles of a choice must occur in receiver position
    # (i.e. be "enabled" -- the at-role is enabled implicitly) before occuring in
    # any non- transfer-receiver position, such as a nested choice at-position
    # here)
    if not context.is_role_enabled(src):
        util.report_error("Role not enabled: " + src)

    # Destination roles
    tmp = []
    for dest in dests:
        # Section 4.6.5 -- bound destination roles
        if not context.is_role_declared(dest):
            util.report_error("Bad destination role: " + dest)
        if dest in tmp:  # Section 4.6.5 -- distinct destination roles
            util.report_error("Duplicate destination role: " + dest)
        tmp.append(dest)


# FIXME: what is scope of operators? global over module? unlike roles,
# parameters, payload types, etc. (even protocols)
def check_wellformedness_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    src = get_source(node_)
    dests = get_destinations(node_)

    if src == projector.role or projector.role in dests:
        child = get_message_child(node_)
        message = None
        if util.get_node_type(child) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            message = messagesignature_pretty_print(child)  # FIXME: string hack
        else:
            message = parameter_get_name(child)  # FIXME: string hack

        if src == projector.role:
            if projector.role in dests:
                util.report_error("Self communication not supported.")
            #new_dests = util.replace_in_list(dests, projector.rolemap)
            new_dests = dests
            return projector.nf.localsend(projector.role, new_dests, message)
        if projector.role in dests:
            if src == projector.role:
                util.report_error("Self communication not supported.")
            #new_src = util.replace_in_list([src], projector.rolemap)[0]
            new_src = src
            return projector.nf.localreceive(projector.role, new_src, message)
    else:
        return None  # OK to use None as "empty projection"?


def get_source(node_):
    return role_get_name(get_source_child(node_))

def get_destinations(node_):
    dests = []
    for child in get_destination_children(node_):
        dests.append(role_get_name(child))
    return dests


def pretty_print(node_):
    text = ""
    message = get_message_child(node_)
    if util.get_node_type(message) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        text = text + messagesignature_pretty_print(message)
    else:
        text = text + parameter_pretty_print(message)
    text = text + ' ' + constants.FROM_KW + ' '
    text = text + get_source(node_)
    text = text + ' ' + constants.TO_KW + ' '
    dests = get_destinations(node_)
    text = text + dests[0]
    for dest in dests[1:]:
        text = text + ', ' + dest
    text = text + ';'
    return text


def get_message_child(node_):
    return node_.getChild(MESSAGE_INDEX)

def get_source_child(node_):
    return node_.getChild(SENDER_INDEX)

def get_destination_children(node_):
    return node_.getChildren()[FIRST_RECEIVER_INDEX:]
