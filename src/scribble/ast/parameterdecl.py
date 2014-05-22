import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node

from ast.parameter import get_parameter_name as parameter_get_name


KIND_INDEX = 0
NAME_INDEX = 1
ALIAS_INDEX = 2


class ParameterDecl(Node):
    #kind = None # Constants KIND
    #name = None  # string
    #alias = None  # string

    def __init__(self, kind, name, alias):
        super(ParameterDecl, self).__init__()
        self.kind = kind
        self.name = name
        self.alias = alias

    def pretty_print(self):
        kind = parameter_kind_to_string(self.kind)
        # self.alias is None for no alias
        return _pretty_print_aux(kind, self.name, self.alias)

    def has_alias(self):
        return self.alias is not None


def project(projector, node_):
    kind = get_kind(node_)
    name = get_parameter_name(node_)
    alias = None
    if has_alias(node_):
        alias = get_alias_name(node_)
    return projector.nf.parameterdecl(kind, name, alias)



def has_alias(node_):
    return node_.getChildCount() > 2  # Factor out constant?

def get_kind(node_):
    return get_kind_child(node_).getText()  # HACK? keyword value (type/sig)

def get_parameter_name(node_):
    return parameter_get_name(get_parameter_child(node_))

def get_alias_name(node_):
    return parameter_get_name(get_alias_child(node_))

# Section 4.1 -- parameter declaration name
def get_declaration_name(node_):
    if has_alias(node_):
        return get_alias_name(node_)
    else:
        return get_parameter_name(node_)


def pretty_print(node_):
    kind = parameter_kind_to_string(get_kind(node_))
    name = get_parameter_name(node_)
    alias = None
    if has_alias(node_):
        alias = get_alias_name(node_)
    return _pretty_print_aux(kind, name, alias)

def _pretty_print_aux(kind, name, alias):
    text = kind
    text = text + ' ' + name
    if alias is not None:
        text = text + ' as ' + alias
    return text


# Probably belongs somewhere else
def parameter_kind_to_string(kind):
    if kind == constants.KIND_MESSAGE_SIGNATURE:
        return constants.SIG_KW
    elif kind == constants.KIND_PAYLOAD_TYPE:
        return constants.TYPE_KW
    else:
        util.report_error("Unknown parameter kind: ", kind)


def get_kind_child(node_):
    return node_.getChild(KIND_INDEX)

def get_parameter_child(node_):
    return node_.getChild(NAME_INDEX)

def get_alias_child(node_):
    return node_.getChild(ALIAS_INDEX)
