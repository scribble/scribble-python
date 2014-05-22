import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node

from ast.role import get_role_name as role_get_name;


ARGUMENT_INDEX = 0
PARAMETER_INDEX = 1


class RoleInstantiation(Node):
    #arg = None  # string
    #param = None  # string

    def __init__(self, arg, param):
        super(RoleInstantiation, self).__init__()
        self.arg = arg
        self.param = param


def traverse(traverser, node_):
    traversed = []
    traversed.append(traverser.traverse_untyped_leaf(get_arg_child(node_)))
    if has_parameter_child(node_):    
        param = get_parameter_child(node_)
        traversed.append(traverser.traverse_untyped_leaf(param))
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def get_arg(node_):
    return role_get_name(get_arg_child(node_))

def get_parameter(node_):
    if has_parameter_child(node_):
        return role_get_name(get_parameter_child(node_))
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
