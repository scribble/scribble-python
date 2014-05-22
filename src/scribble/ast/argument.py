import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node

from ast.messagesignature import pretty_print as messagesignature_pretty_print
from ast.parameter import get_parameter_name as parameter_get_name


ARGUMENT_INDEX = 0
PARAMETER_INDEX = 1


class Argument(Node):
    #kind = None # Constants KIND
    #is_val = None # boolean (True if value, False if parameter)
    #arg = None  # messagesignature or string
    #param = None  # string

    def __init__(self, kind, is_val, arg, param):
        super(Argument, self).__init__()
        self.kind = kind
        self.is_val = is_val
        self.arg = arg
        self.param = param


def traverse(traverser, node_):
    traversed = []
    arg = get_arg_child(node_)
    if util.get_node_type(arg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        traversed.append(traverser.traverse(arg))
    else:
        traversed.append(traverser.traverse_untyped_leaf(arg))
    if has_parameter_child(node_):    
        param = get_parameter_child(node_)
        traversed.append(traverser.traverse_untyped_leaf(param))
    new = util.antlr_dupnode_and_replace_children(node_, traversed)
    return new


def get_arg(node_):
    arg = get_arg_child(node_)
    if util.get_node_type(arg) == constants.MESSAGE_SIGNATURE_NODE_TYPE:
        # FIXME: broken if type/parameter name happens to be 'MESSAGESIGNATURE'
        return messagesignature_pretty_print(arg)  # Is this right?
    else:
        return arg.getText()  # payload type or parameter name

def get_parameter(node_):
    if has_parameter_child(node_):
        return parameter_get_name(get_parameter_child(node_))
    else:
        return None


def pretty_print(node_):
    text = get_arg(node_)
    if has_parameter_child(node_):
        text = text + ' as ' + get_parameter(node_)
    return text


# Decl version doesn't have Child suffix
def has_parameter_child(node_):
    return node_.getChildCount() > 1

def get_arg_child(node_):
    return node_.getChild(ARGUMENT_INDEX)

def get_parameter_child(node_):
    return node_.getChild(PARAMETER_INDEX)
