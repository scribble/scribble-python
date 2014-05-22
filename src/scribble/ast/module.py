import scrib_collections as collections
import scrib_constants as constants
import scrib_util as util

from ast.node import Node as Node

from ast.importmodule import (
    get_declaration_name as importmodule_get_declaration_name,
    pretty_print as importmodule_pretty_print,
    get_full_module_name as importmodule_get_full_name
)

from ast.moduledecl import (
    get_full_name as moduledecl_get_full_name,
    pretty_print as moduledecl_pretty_print
)

from ast.payloadtypedecl import (
    get_declaration_name as payloadtypedecl_get_declaration_name,
    pretty_print as payloadtypedecl_pretty_print
)

#from ast.globel.globalprotocoldecl import (
#    get_name as globalprotocoldecl_get_name,
#    pretty_print as globalprotocoldecl_pretty_print
#)

from ast.local.localprotocoldecl import (
    get_name as localprotocoldecl_get_name,
    pretty_print as localprotocoldecl_pretty_print
)


MODULEDECL_CHILD_INDEX = 0


def get_moduledecl_child(node_):
    #check_module_node_type(node_)
    return node_.getChild(MODULEDECL_CHILD_INDEX)


# Moved below "get_moduledecl_child" to resolve circular import
#
from ast.globel.globalprotocoldecl import (
    get_name as globalprotocoldecl_get_name,
    pretty_print as globalprotocoldecl_pretty_print
)


class Module(Node):
    #decl = None  # moduledecl
    #imports = None # [ ImportDecl ]
    ##importmodules = None  # [ importmodule ]
    ##importmembers = None  # [ ImportMember ]
    #payloads = None  # [ payloadtypedecl ]
    #globalps = None  # [ globalprotocoldecl ]
    #localps = None  # [ localprotocoldecl ]

    #def __init__(self, decl, importmodules, importmembers, payloads, globalps, localps):
    def __init__(self, decl, imports, payloads, globalps, localps):
        super(Module, self).__init__()
        self.decl = decl
        #self.importmodules = importmodules
        #self.importmembers = importmembers
        self.imports = imports
        self.payloads = payloads
        self.globalps = globalps
        self.localps = localps
    
    def get_full_name(self):
        return self.decl.get_full_name()

    # For projection
    def addlocalprotocoldecl(self, lpd):
        clone = self.clone()
        clone.localps.append(lpd)
        return clone

    def clone(self):
        # Use node factory? (add as a field to node)
        decl = self.decl  # immutable?
        imports = collections.clone_collection(self.imports)
        payloads = collections.clone_collection(self.payloads)
        globalps = collections.clone_collection(self.globalps)
        localps = collections.clone_collection(self.localps)
        clone = Module(self.decl, imports, payloads, globalps, localps)
        return clone

    # FIXME: integrate with the "static" ANTLR-bsaed method
    def pretty_print(self):
        text = ''
        text = text + self.decl.pretty_print()
        text = text + '\n\n'
        for im in self.imports:  # FIXME: also members
            text = text + im.pretty_print() + '\n'
        text = text + '\n\n'
        for ptd in self.payloads:
            text = text + ptd.pretty_print() + '\n\n'
        for gpd in self.globalps:
            text = text + gpd.pretty_print() + '\n\n'
        for lpd in self.localps:
            text = text + lpd.pretty_print()
        return text


def traverse(traverser, node_):
    traversed = []
    moduledecl = get_moduledecl_child(node_)
    traversed.append(traverser.traverse(moduledecl))
    for im in get_importmodule_children(node_):
        traversed.append(traverser.traverse(im))
    for im in get_importmember_children(node_):
        util.report_error("Member Import not supported yet.")
      # FIXME: also members
    for ptd in get_payloadtypedecl_children(node_):
        traversed.append(traverser.traverse(ptd))
    for gpd in get_globalprotocoldecl_children(node_):
        traversed.append(traverser.traverse(gpd))
    for lpd in get_localprotocoldecl_children(node_):
        traversed.append(traverser.traverse(lpd))
    # rebuild using new children
    return util.antlr_dupnode_and_replace_children(node_, traversed)


def check_wellformedness_enter(checker, node_):
    checker.enter(node_)


##
# FIXME: can factor out to a general visit routine for all Visitors (traverse)
def check_wellformedness_visit(checker, node_):
    ##
    # Section 4.2 -- Simple name and filename of module condition checked in moduledecl_ (also currently checked earlier by moduleLoader)

    ##
    # Section 4.2 -- Distinct module names condition
    fmn = moduledecl_get_full_name(get_moduledecl_child(node_))
    smn_from_fmn = util.get_simple_module_name_from_full_module_name(fmn)
    names = [smn_from_fmn]
    for im in get_importmodule_children(node_):
        name = importmodule_get_declaration_name(im)
        if name in names:
            util.report_error("Bad module import declaration name: " + name)
        names.append(name)

    ##
    # Section 4.2 -- Distinct member names condition
    names = []
    for ptd in get_payloadtypedecl_children(node_):
        name = payloadtypedecl_get_declaration_name(ptd)
        if name in names:
            util.report_error("Bad payload type declaration name: " + name)
        names.append(name)
    for gpd in get_globalprotocoldecl_children(node_):
        name = globalprotocoldecl_get_name(gpd)
        if name in names:
            util.report_error("Bad global protocol declaration name: " + name)
        names.append(name)
    for lpd in get_localprotocoldecl_children(node_):
        name = localprotocoldecl_get_name(lpd)
        if name in names:
            util.report_error("Bad local protocol declaration name: " + name)
        names.append(name)
    for im in get_importmember_children(node_):
        # TODO: import member declaration names
        util.report_error("TODO member import: " + im)

    ##
    # Section 4.2 -- Well-formed import declarations and members
    #
    # Same visiting structure as traverse; in the general case, however,
    # well-formedness visiting needs to visit each child with a separate
    # context, so cannot directly reuse the traverse routine here
    visited = []
    moduledecl_ = get_moduledecl_child(node_)
    visited.append(checker.visit(moduledecl_))
    for im in get_importmodule_children(node_):
        visited.append(checker.visit(im))
    for im in get_importmember_children(node_):
        util.report_error("Member Import not supported yet.")
      # FIXME: also members
    for ptd in get_payloadtypedecl_children(node_):
        visited.append(checker.visit(ptd))
    for gpd in get_globalprotocoldecl_children(node_):
        visited.append(checker.visit(gpd))
    for lpd in get_localprotocoldecl_children(node_):
        #visited.append(checker.visit(lpd))
        # TODO
        util.report_warning("[WellformednessChecker] Skipping localprotocoldecl: " \
                            + localprotocoldecl_get_name(lpd))
        #print "Skipped:\n", localprotocoldecl_pretty_print(lpd)
    # rebuild using new children
    return util.antlr_dupnode_and_replace_children(node_, visited)


def check_wellformedness_leave(checker, node_):
    checker.leave(node_)


# this is not a "full projection", it prepares a module to contain a projected
# global protocol
#
# anode is ANTLR node_
def project(projector, node_):
    localtarget = projector.local_target
    subprotos = projector.subprotocols

    target_localmodulename = localtarget[:localtarget.rfind('.')]    
        # Can also derive from (global) node_
    decl = projector.nf.moduledecl(target_localmodulename)
    imports = []
    payloads = []
    
    lpd = projector.context.get_projection(localtarget)

    subprotos = projector.collect_subprotocols(projector.context, lpd.get_body().get_block())
    module_refs = []
    for sp in subprotos:
        module_refs.append(util.get_global_module_name_from_projected_member_name(sp))

    for id in get_importdecl_children(node_):
        if util.get_node_type(id) == constants.IMPORT_MODULE_NODE_TYPE:
            if importmodule_get_full_name(id) in module_refs:
                tmp = projector.visit(id)
                if tmp != None:
                    imports.append(tmp)
        else:
            raise RuntimeError("TODO: " + id)
        
    # Additional imports to insert due to co-module protocols being projected
    # into separate output modules
    target_globalmodulename = \
        util.get_global_module_name_from_projected_member_name(localtarget)
    # sp is the local subprotocol name
    for sp in subprotos:
        if sp != localtarget:
            gmn = util.get_global_module_name_from_projected_member_name(sp)
            if gmn == target_globalmodulename:
                    # Subprotocol is a global co-module protocol of the target
                lmn = util.get_full_module_name_from_full_member_name(sp)
                im = projector.nf.importmodule(lmn, None)
                imports.append(im)

    for ptd in get_payloadtypedecl_children(node_):
        payloads.append(projector.visit(ptd))

    # Creating the local module "shell"
    return projector.nf.module(decl, imports, payloads, [], [])


def get_full_name(node_):
    return moduledecl_get_full_name(get_moduledecl_child(node_))


# TODO: factor out with above object method
def pretty_print(node_):
    text = ''
    text = text + moduledecl_pretty_print(get_moduledecl_child(node_))
    text = text + '\n\n'
    for im in get_importmodule_children(node_):  # FIXME: also members
        text = text + importmodule_pretty_print(im) + '\n'
    text = text + '\n\n'
    for ptd in get_payloadtypedecl_children(node_):
        text = text + payloadtypedecl_pretty_print(ptd) + '\n\n'
    for gpd in get_globalprotocoldecl_children(node_):
        text = text + globalprotocoldecl_pretty_print(gpd) + '\n\n'
    """for lpd in get_localprotocoldecl_children(node_):
        text = text + ....pretty_print(lpd) + '\n\n'"""  # TODO
    return text

def check_module_node_type(node_):
    type = util.get_node_type(node_)
    if util.get_node_type(node_) != constants.MODULE_NODE_TYPE:
        raise Exception("Expected " + constants.MODULE_NODE_TYPE + \
                        " type, not: " + type)



def get_importdecl_children(node_):
    res = []
    for node_ in node_.getChildren():
        ntype = util.get_node_type(node_)
        if ntype == constants.IMPORT_MODULE_NODE_TYPE or \
                    ntype == constants.IMPORT_MEMBER_NODE_TYPE:
            res.append(node_)
    return res

def get_importmodule_children(node_):
    check_module_node_type(node_)
    return util.filter_node_types(node_.getChildren(),
                                  constants.IMPORT_MODULE_NODE_TYPE)

def get_importmember_children(node_):
    check_module_node_type(node_)
    return util.filter_node_types(node_.getChildren(),
                                  constants.IMPORT_MEMBER_NODE_TYPE)

def get_payloadtypedecl_children(node_):
    check_module_node_type(node_)
    return util.filter_node_types(node_.getChildren(),
                                  constants.PAYLOAD_DECL_NODE_TYPE)

def get_globalprotocoldecl_children(node_):
    check_module_node_type(node_)
    return util.filter_node_types(node_.getChildren(),
                                  constants.GLOBAL_PROTOCOL_DECL_NODE_TYPE)

def get_localprotocoldecl_children(node_):
    check_module_node_type(node_)
    return util.filter_node_types(node_.getChildren(),
                                  constants.LOCAL_PROTOCOL_DECL_NODE_TYPE)
