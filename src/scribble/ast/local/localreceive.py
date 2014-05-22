import scrib_constants as constants
import scrib_util as util

from ast.messagesignature import \
    pretty_print as messagesignature_pretty_print
from ast.parameter import \
    pretty_print as parameter_pretty_print
from ast.role import get_role_name as role_get_role_name

from ast.local.localnode import LocalNode as LocalNode


MESSAGE_INDEX = 0
SENDER_INDEX = 1


class LocalReceive(LocalNode):
    #src = None     # String
    #message = None # String  # FIXME: currently not shared with global

    def __init__(self, local_role, src, message):
        super(LocalReceive, self).__init__(local_role)
        self.src = src
        self.message = message

    def get_source(self):
        return self.src

    def get_message(self):
        return self.message

    def pretty_print(self):
        message = self.get_message()
        text = self.message
        text = text + ' ' + constants.FROM_KW + ' '
        text = text + self.src
        text = text + ';'
        return text


def traverse(traverser, node_):
    traversed = []
    msg = get_message_child(node_)
    if util.get_node_type(msg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        traversed.append(traverser.traverse(msg))
    else:
        traversed.append(traverser.traverse_untyped_leaf(msg))
    traversed.append(traverser.traverse_untyped_leaf(get_source_child(node_)))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def get_source(node_):
    return role_get_role_name(get_source_child(node_))


def pretty_print(node_):
    text = ''
    message = get_message_child(node_)
    if util.get_node_type(message) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        text = text + messagesignature_pretty_print(message)
    else:
        text = text + parameter_pretty_print(message)
    text = text + ' ' + constants.FROM_KW + ' '
    text = text + get_source(node_)
    text = text + ';'
    return text


def get_message_child(node_):
    return node_.getChild(MESSAGE_INDEX)

def get_source_child(node_):
    return node_.getChild(SENDER_INDEX)


