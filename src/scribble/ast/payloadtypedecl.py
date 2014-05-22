import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node


KIND_INDEX = 0
EXTERNAL_TYPE_NAME_INDEX = 1
EXTERNAL_SOURCE_INDEX = 2
DECLARATION_NAME_INDEX = 3


class payloadTypeDecl(Node):
    #kind = None  # String
    #ext_name = None  # String
    #source = None  # String
    #decl_name = None  # String

    def __init__(self, kind, ext_name, source, decl_name):
        super(payloadTypeDecl, self).__init__()
        self.kind = kind
        self.ext_name = ext_name
        self.source = source
        self.decl_name = decl_name

    def pretty_print(self):
        text = ''
        text = text + constants.TYPE_KW + ' '
        text = text + '<' + self.kind + '>' + ' '
        #text = text + '"' + self.ext_name + '"' + ' '
        text = text + ' ' + self.ext_name + ' '
        #text = text + constants.FROM_KW + ' "' + self.source + '"' + ' '
        text = text + constants.FROM_KW + ' ' + self.source + ' '
        text = text + constants.AS_KW + ' ' + self.decl_name + ';'
        return text


def project(projector, node_):
    kind = get_kind(node_)
    ext_name = get_external_type(node_)
    source = get_external_source(node_)
    decl_name = get_declaration_name(node_)
    new = projector.nf.payloadtypedecl(kind, ext_name, source, decl_name)
    return new


##
# Section 4.3 TODO (in language reference)
def check_wellformedness_enter(checker, node_):
    pass
    # relies on MemberLoader being run first. OK to have this pass dependency?

def check_wellformedness_visit(checker, node_):
    pass

def check_wellformedness_leave(checker, node_):
    pass


def traverse(traverser, node_):
    return node_


def get_kind(node_):
    return get_kind_child(node_).getText()

def get_external_type(node_):
    return get_external_type_child(node_).getText()

def get_external_source(node_):
    return get_source_child(node_).getText()

def get_declaration_name(node_):
    return get_declaration_name_child(node_).getText()


def pretty_print(node_):
    text = ""
    text = text + constants.TYPE_KW + ' '
    text = text + '<' + get_kind(node_) + '>' + ' '
    text = text + '"' + get_external_type(node_) + '"' + ' '
    text = text + constants.FROM_KW + ' "'
    text = text + get_external_source(node_) + '"' + ' '
    text = text + constants.AS_KW + ' "'
    text = text + get_declaration_name(node_) + ';'
    return text


def get_kind_child(node_):
    return node_.getChild(KIND_INDEX)

def get_external_type_child(node_):
    return node_.getChild(EXTERNAL_TYPE_NAME_INDEX)

def get_source_child(node_):
    return node_.getChild(EXTERNAL_SOURCE_INDEX)

def get_declaration_name_child(node_):
    return node_.getChild(DECLARATION_NAME_INDEX)
