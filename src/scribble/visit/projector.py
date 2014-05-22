import scrib_constants as constants
import scrib_util as util

from visit.visitor import Visitor as Visitor

from visit.rolecollector import RoleCollector

from visit.subprotocolcollector import SubprotocolCollector

from ast.nodefactory import NodeFactory as NodeFactory

#import ast.ImportMember as ImportMember
from ast.importmodule import project as importmodule_project
from ast.module import project as module_project

from ast.module import (
    pretty_print as module_pretty_print,
    get_full_name as module_get_full_name,
    project as module_project
)

from ast.moduledecl import project as moduledecl_project
from ast.parameterdecl import project as parameterdecl_project
from ast.parameterdecllist import project as parameterdecllist_project
from ast.payloadtypedecl import project as payloadtypedecl_project
from ast.roledecl import project as roledecl_project
from ast.roledecllist import project as roledecllist_project

from ast.globel.globalprotocoldecl import (
    get_name as globalprotocoldecl_get_name,
    project as globalprotocoldecl_project
)

from ast.globel.globalprotocoldef import project as globalprotocoldef_project
from ast.globel.globalprotocolblock import \
    project as globalprotocolblock_project
from ast.globel.globalinteractionsequence import \
    project as globalinteractionsequence_project
from ast.globel.globalmessagetransfer import \
    project as globalmessagetransfer_project
from ast.globel.globalchoice import project as globalchoice_project
from ast.globel.globalrecursion import project as globalrecursion_project
from ast.globel.globalcontinue import project as globalcontinue_project
from ast.globel.globalparallel import project as globalparallel_project
from ast.globel.globalinterruptible import \
    project as globalinterruptible_project
from ast.globel.globaldo import project as globaldo_project


# Like the other Visitors, the pattern is the "named" (entry) method (i.e.
# "project_globalprotocoldecl" -- cf.\ "check_wellformedness") is used once at the
# top level by the outside user, and internally within the traversal routines we
# use the "visit" methods of the Visitor (which calls the node-specific
# "project" methods)
#
# Similar traversal pattern as Visitor, but visit returns local types not global
# types. but Python isn't typed so can reuse base class
#
# Traversal pattern differs from normal Visitor in that projection of a module
# creates an empty module skeleton -- have to manually add the projected members
#
# Stores a context like ContextVisitor, but it is a global static, not modified
# during traversal like ContextVisitor -- could be made into a ContextVisitor,
# with the above modified traversal pattern
#
# Could use Traverser pattern
class Projector(Visitor):
    nf = NodeFactory()

    # Here because inconvenient to import in the ast modules
    rc = RoleCollector()

    #context = None  # Context
    #role = None  # string  # set by the project method
    #currentmodule = None  # string (fmn)  # is this needed?
    #currentprotocol = None  # string (smn)

    # The Context should have modules loaded and visibility built etc. (uniform
    # with WellformednessChecker)
    """def __init__(self, context_, role_):
        super(Projector, self).__init__()
        self.context = context_
        self.role = role_  # string
        #self._protocol = None
        self._todo = [] # [(string, string)] 
            #(visible) target _protocol name, role_ param 
            # Should be treated as a set"""
    def __init__(self):
        super(Projector, self).__init__()
        #self.context = context_
        #self.role = role_  # string
        self._todo = [] # [(string, string)] 
            #(visible) target _protocol name, role_ param 
            # Should be treated as a set

    
    def project(self, context_, node_, role_):#, rolemap):
        self.context = context_
        self.role = role_
        #self.rolemap = {}
        #self.rolemap[role_] = role_
        return self.visit(node_)

    """def project_globalprotocoldecl(self, gpd):
        self._protocol = globalprotocoldecl_get_name(gpd)
            # simple (declaration) name
        lpd = self.visit(gpd)
        module_ = gpd.getParent() 
            # Alternatively parse module_ name from _protocol name
        lm = self.visit(module_)
        lm = lm.addlocalprotocoldecl(lpd)
        return lm"""
    
    # "globalmodule" means the module containing the global being projected
    def project_module(self, context_, globalmodule, target_localname, subprotos):
        self.context = context_
        self.local_target = target_localname 
        self.subprotocols = subprotos
        return self.visit(globalmodule)

    def project_globalprotocoldecl(self, context_, gpd, role_):#, rolemap):
        self._protocol = globalprotocoldecl_get_name(gpd)
            # simple (declaration) name
        return self.project(context_, gpd, role_)#, rolemap)
    
    
    # Here because of cyclic imports (in module)
    def collect_subprotocols(self, context_, node_):
        return SubprotocolCollector(context_).collect_subprotocols(node_, False)


    """def get_context(self):
        return self._context
    
    def set_context(self, context_):
        self._context = context"""

    def get_protocol(self):
        return self._protocol
        
    """def get_role(self):
        return self._role
    
    def set_role(self, role_):
        self._role = role_"""

    """def get_subprotocol_references(self):
        return self._todo

    def add_subprotocol_reference(self, target, role_):
        if (target, role_) not in self._todo:
            self._todo.append((target, role_))"""


    def _visit_module(self, node_):
        return module_project(self, node_)
        #raise RuntimeError("Shouldn't get in here: ")

    def _visit_moduledecl(self, node_):
        return moduledecl_project(self, node_)

    def _visit_importmodule(self, node_):
        return importmodule_project(self, node_)

    def _visitImportMember(self, node_):
        return ImportMember_project(self, node_)

    def _visit_payloadtypedecl(self, node_):
        return payloadtypedecl_project(self, node_)

    def _visit_globalprotocoldecl(self, node_):
        return globalprotocoldecl_project(self, node_)

    def _visit_roledecllist(self, node_):
        return roledecllist_project(self, node_)

    def _visit_roledecl(self, node_):
        return roledecl_project(self, node_)

    def _visit_parameterdecllist(self, node_):
        return parameterdecllist_project(self, node_)

    def _visit_parameterdecl(self, node_):
        return parameterdecl_project(self, node_)

    def _visit_roleinstantiationlist(self, node_):
        return roleinstantiationlist_project(self, node_)

    def _visit_roleinstantiation(self, node_):
        return roleinstantiation_project(self, node_)

    def _visit_argumentlist(self, node_):
        return argumentlist_project(self, node_)

    def _visit_argument(self, node_):
        return argument_project(self, node_)


    def _visit_globalprotocoldef(self, node_):
        return globalprotocoldef_project(self, node_)

    def _visit_globalprotocolblock(self, node_):
        return globalprotocolblock_project(self, node_)

    def _visit_globalinteractionsequence(self, node_):
        return globalinteractionsequence_project(self, node_)

    def _visit_globalmessagetransfer(self, node_):
        return globalmessagetransfer_project(self, node_)

    def _visit_globalchoice(self, node_):
        return globalchoice_project(self, node_)

    def _visit_globalrecursion(self, node_):
        return globalrecursion_project(self, node_)

    def _visit_globalcontinue(self, node_):
        return globalcontinue_project(self, node_)

    def _visit_globalparallel(self, node_):
        return globalparallel_project(self, node_)

    def _visit_globalinterruptible(self, node_):
        return globalinterruptible_project(self, node_)

    def _visit_globalinterrupt(self, node_):
        return globalinterrupt_project(self, node_)

    def _visit_globaldo(self, node_):
        return globaldo_project(self, node_)
