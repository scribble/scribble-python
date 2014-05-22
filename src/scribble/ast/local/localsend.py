import scrib_constants as constants
import scrib_util as util

from ast.messagesignature import \
    pretty_print as messagesignature_pretty_print
from ast.parameter import \
    pretty_print as parameter_pretty_print
from ast.role import get_role_name as role_get_role_name

from ast.local.localnode import LocalNode as LocalNode


MESSAGE_INDEX = 0
FIRST_RECEIVER_INDEX = 1


class LocalSend(LocalNode):
    #dests = None    # [ String ]
    #message = None # String  # FIXME: currently not shared with global

    def __init__(self, local_role, dests, message):
        super(LocalSend, self).__init__(local_role)
        self.dests = dests
        self.message = message

    def get_destinations(self):
        return self.dests

    def get_message(self):
        return self.message

    def pretty_print(self):
        text = ""
        message = self.get_message()
        text = text + self.message
        text = text + ' ' + constants.TO_KW + ' '
        text = text + self.dests[0]
        for dest in self.dests[1:]:
            text = text + ', ' + dest
        text = text + ';'
        return text


def traverse(traverser, node_):
    traversed = []
    msg = get_message_child(node_)
    if util.get_node_type(msg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        traversed.append(traverser.traverse(msg))
    else:
        traversed.append(traverser.traverse_untyped_leaf(msg))
    for dest in get_destination_children(node_):
        traversed.append(traverser.traverse_untyped_leaf(dest))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def get_destinations(node_):
    dests = []
    for child in get_destination_children(node_):
        dests.append(role_get_role_name(child))
    return dests


def pretty_print(node_):
    text = ""
    message = get_message_child(node_)
    if util.get_node_type(message) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        text = text + messagesignature_pretty_print(message)
    else:
        text = text + parameter_pretty_print(message)
    text = text + ' ' + constants.TO_KW + ' '
    dests = get_destinations(node_)
    text = text + dests[0]
    for dest in dests[1:]:
        text = text + ', ' + dest
    text = text + ';'
    return text


def get_message_child(node_):
    return node_.getChild(MESSAGE_INDEX)

def get_destination_children(node_):
    return node_.getChildren()[FIRST_RECEIVER_INDEX:]


def context_visitor_visit(cv, node_):
    # Not recording ops, unlike global contexts
    pass


"""def context_visitor_visit(cv, node_):
    return node_


def context_visitor_leave(cv, node_):
    pass


def check_reachability_enter(checker, node_):
    pass


def check_reachability_visit(checker, node_):
    return context_visitor_visit(checker, node_)


def check_reachability_leave(checker, node_):
    pass"""
