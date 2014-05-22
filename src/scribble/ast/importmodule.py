import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node


OPTIONAL_ALIAS_INDEX = 0


class ImportModule(Node):
    #fmn = None  # String
    #alias = None  # String

    #def __init__(self, decl, importmodules, importmembers, payloads, globalps, localps):
    def __init__(self, fmn, alias):
        super(ImportModule, self).__init__()
        self.fmn = fmn
        self.alias = alias

    def pretty_print(self):
        text = constants.IMPORT_KW + ' ' + self.fmn
        if self.has_alias():
            text = text + ' as ' + self.alias
        text = text + ';'
        return text

    def has_alias(self):
        return self.alias != None


def traverse(traverser, node_):
    return node_


def check_wellformedness_enter(checker, node_):
    pass

def check_wellformedness_visit(checker, node_):
    return node_

def check_wellformedness_leave(checker, node_):
    pass


def project(projector, node_):
    projections = projector.context.get_projections()
    fmn = get_full_module_name(node_)
    
    # Check if this import is referring to one of the subprotocol modules.
    # "target" is the local target name
    #
    # FIXME: make precise about which subprotocols are actually needed (use
    # SubprotocolCollector again for the current target)
    for target in projector.subprotocols:
        gmn = util.get_global_module_name_from_projected_member_name(target)
        if fmn == gmn:
            if not has_alias(node_):
                localmodulename = \
                    util.get_full_module_name_from_full_member_name(target)
                return projector.nf.importmodule(localmodulename, None) 
            else:
                util.report_error("[Projector] importmodule TODO: " + \
                                  get_declaration_name(node_))
        #else:
        #    util.report_error("[Projector] importmodule TODO: " + target)"""
    return None


def has_alias(node_):
    return util.get_node_type(node_.getChild(OPTIONAL_ALIAS_INDEX)) \
               == constants.AS_KW


def get_full_module_name(node_):
    # HACK?
    index = 0
    if has_alias(node_):
        index = 2
    fqpn = node_.getChild(index).getText()
    remaining = node_.getChildren()[index+1:]
    for tmp in remaining:
        fqpn = fqpn + '.' + tmp.getText()
    return fqpn


##
# Section 4.1 -- Imported module declaration name
def get_declaration_name(node_):
    if has_alias(node_):
        return node_.getChild(OPTIONAL_ALIAS_INDEX+1).getText()
    else:
        return get_full_module_name(node_)


def pretty_print(node_):
    text = constants.IMPORT_KW + ' ' + get_full_module_name(node_)
    if has_alias(node_):
        text = text + ' as ' + get_declaration_name(node_)
    text = text + ';'
    return text
