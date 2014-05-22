import scrib_constants as constants
import scrib_util as util

from ast.messagesignature import \
    pretty_print as messagesignature_pretty_print
from ast.role import get_role_name as role_get_role_name
from ast.parameter import \
    pretty_print as parameter_pretty_print

from ast.local.localnode import LocalNode as LocalNode


SENDER_INDEX = 0
FIRST_MESSAGE_INDEX = 1


# Can factor out a lot with localthrow
class LocalCatch(LocalNode):
    #src = None      # String (role name)  -- using Strings, as in localsend
    #messages = None # [ String ]  # Messasge signature or parameter

    def __init__(self, local_role, src, messages):
        super(LocalCatch, self).__init__(local_role)
        self.src = src
        self.messages = messages

    def get_source(self):
        return self.src

    def get_messages(self):
        return self.messages

    def pretty_print(self):
        text = ""
        text = text + constants.CATCHES_KW + ' ';
        text = text + self.messages[0]
        for msg in self.messages[1:]:
            text = text + ', ' + msg
        text = text + ' ' + constants.FROM_KW + ' '
        text = text + self.src
        text = text + ';'
        return text


def traverse(traverser, node_):
    traversed = []
    src = get_source_child(node_)
    traversed.append(traverser.traverse_untyped_leaf(src))
    for msg in get_message_children(node_):
        if util.get_node_type(msg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            traversed.append(traverser.traverse(msg))
        else:
            traversed.append(traverser.traverse_untyped_leaf(msg))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def get_source(node_):
    return role.get_role_name(get_source_child(node_))


def pretty_print(node_):
    text = ""
    messages = get_message_children(node_)
    text = text + _pretty_print_aux(messages[0])
    for msg in messages[1:]:
        text = text + ', ' + _pretty_print_aux(msg)
    text = text + ' ' + constants.FROM_KW + ' '
    text = text + get_source(node_)
    text = text + ';'
    return text

def _pretty_print_aux(msg):  # Factor out more globally (also in localthrow)
    if util.get_node_type(msg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        return messagesignature_pretty_print(msg)
    else:
        return parameter_pretty_print(msg)


def get_source_child(node_):
    return node_.getChild(SENDER_INDEX)

def get_message_children(node_):
    return node_.getChildren()[FIRST_MESSAGE_INDEX:]
