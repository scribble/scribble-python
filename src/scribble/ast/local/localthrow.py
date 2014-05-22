import scrib_constants as constants
import scrib_util as util

from ast.messagesignature import \
    pretty_print as messagesignature_pretty_print
from ast.role import get_role_name as role_get_role_name
from ast.parameter import \
    pretty_print as parameter_pretty_print

from ast.local.localnode import LocalNode as LocalNode


FIRST_RECEIVER_INDEX = 0


class LocalThrow(LocalNode):
    #dests = None    # [ String ]  # role names
    #messages = None # [ String ]  # Message sigs or params

    def __init__(self, local_role, dests, messages):
        super(LocalThrow, self).__init__(local_role)
        self.dests = dests
        self.messages = messages

    def get_destinations(self):
        return self.dests

    def get_messages(self):
        return self.messages

    def pretty_print(self):
        text = ""
        text = text + constants.THROWS_KW + ' ';
        text = text + self.messages[0]
        for msg in self.messages[1:]:
            text = text + ', ' + msg
        text = text + ' ' + constants.TO_KW + ' '
        
        if not self.dests:
            raise RuntimeError("Shouldn't get in here: ")
        text = text + self.dests[0]
        for dest in self.dests[1:]:
            text = text + ', ' + dest
        text = text + ';'
        return text


def traverse(traverser, node):
    traversed = []
    for dest in node.getChildren()[:_get_tokw_child_index(node)+1]: 
            # includes TO separator child
        traversed.append(traverser.traverse_untyped_leaf(dest))
    for message in get_message_children(node):
        if util.get_node_type(message) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            traversed.append(traverser.traverse(message))
        else:
            traversed.append(traverser.traverse_untyped_leaf(message))
    new = util.antlr_dupnode_and_replace_children(node, traversed)
    return new


def get_destinations(node):
    dests = []
    for child in get_destination_children(node):
        dests.append(role.get_role_name(child))
    return dests


def pretty_print(node):
    text = ""
    messages = get_message_children(node)
    text = text + _pretty_print_aux(messages[0])
    for msg in messages[1:]:
        text = text + ', ' + pretty_print_aux(msg)
    text = text + ' ' + constants.TO_KW + ' '
    dests = get_destinations(node)
    text = text + dests[0]
    for dest in dests[1:]:
        text = text + ', ' + dest
    text = text + ';'
    return text

def _pretty_print_aux(message):  # Factor out more globally
    if util.get_node_type(message) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        return messagesignature_pretty_print(message)
    else:
        return parameter_pretty_print(message)


def _get_tokw_child_index(node):
    i = 0;
    for child in node.getChildren():
        if child.getText() == constants.TO_KW:
            return i
        i += 1
    raise RuntimeError("Shouldn't get in here: " + node)
            

def get_destination_children(node):
    return node.getChildren()[FIRST_RECEIVER_INDEX:_get_tokw_child_index(node)]

def get_message_children(node):
    first_msg = _get_tokw_child_index(node) + 1
    return node.getChildren()[first_msg:len(node.getChildren())]
