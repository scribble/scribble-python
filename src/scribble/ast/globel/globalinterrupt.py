import scrib_constants as constants
import scrib_util as util

from ast.messagesignature import (
    check_wellformedness as messagesignature_check_wellformedness,
    get_operator as messagesignature_get_operator,
    pretty_print as messagesignature_pretty_print
)

from ast.parameter import get_parameter_name as parameter_get_parameter_name

from ast.role import get_role_name as role_get_name


INTERRUPT_ROLE_INDEX = 0
INTERRUPT_MESSAGES_START_INDEX = 1


def traverse(traverser, node_):
    traversed = []
    traversed.append(traverser.traverse_untyped_leaf(get_role_child(node_)))
    for message in get_message_children(node_):
        if util.get_node_type(message) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            traversed.append(traverser.traverse(message))
        else:
            traversed.append(traverser.traverse_untyped_leaf(message))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def check_wellformedness(checker, node_):
    context_ = checker.get_context()

    sigs = get_message_children(node_)
    subj = get_role(node_)

    # Section 4.6.9 -- bound interrupt role
    if not context_.is_role_declared(subj):
        util.report_error("Bad interrupt role: " + subj)

    tmp = context_.get_operators().items()
    for sig in sigs:
        if util.get_node_type(sig) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            #tmp = context_.get_operators().items()
            # Section 4.6.9 -- well-formed message signature
            messagesignature_check_wellformedness(checker, sig)
            op = context_.get_current_scope() + '.' \
                 + messagesignature_get_operator(sig) 
                    # interrupt sig belongs to the scope of the interruptible
            for (src, _), ops in tmp:
                if op in ops:
                    # Section 4.6.9 -- op is not in any potential ops set of
                    # block for subj
                    if subj == src:
                        util.report_error("Bad interrupt operator: " + op)
                    #context_ = context_.add_operator()
                        # FIXME: can't do currently: interrupt messages have no
                        # specific dest (need to look up all possible
                        # destinations, or could make a special broadcast value
                        # constant?) -- top-level interruptible inside a choice
                        # block can also be an enabling op
        else:
            raise RuntimeError("TODO: " + parameter_get_parameter_name(sig))


def get_role(node_):
    return role_get_name(get_role_child(node_))


def pretty_print(node_):
    sigs = get_message_children(node_)
    text = _pretty_print_aux(sigs[0])
    for sig in sigs[1:]:
        text = text + ', '
        text = text + _pretty_print_aux(sig)
    text = text + ' ' + constants.BY_KW + ' '
    text = text + get_role(node_)
    text = text + ';'
    return text

# Factor out with message transfer, argument, etc.
def _pretty_print_aux(sig):
    if util.get_node_type(sig) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        return messagesignature_pretty_print(sig) 
        #text = text + util.pretty_print(sig)
    else:
        # TODO: parameter
        raise RuntimeError("TODO: " + parameter_get_parameter_name(sig))


def get_role_child(node_):
    return node_.getChild(INTERRUPT_ROLE_INDEX)  # node_ type ROLEKW

def get_message_children(node_):
    return node_.getChildren()[INTERRUPT_MESSAGES_START_INDEX:]

"""def getglobalinterruptmessagesignaturesChild(node):
    return node.getChild(0)  # node type SIGKW

def getglobalinterruptmessagesignatureChildren(node):
    return getglobalinterruptmessagesignaturesChild(node).getChildren()

def get_rolesChild(node):
    return node.getChild(1)  # node type ROLEKW

def get_role_children(node):
    return get_rolesChild(node).getChildren()"""
