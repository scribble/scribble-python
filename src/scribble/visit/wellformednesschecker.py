import scrib_util as util

from visit.contextvisitor import ContextVisitor as ContextVisitor
from visit.rolecollector import RoleCollector as RoleCollector

from ast.importmodule import (
    check_wellformedness_enter as importmodule_check_wellformedness_enter,
    check_wellformedness_visit as importmodule_check_wellformedness_visit,
    check_wellformedness_leave as importmodule_check_wellformedness_leave
)

# TODO: import members

from ast.module import ( 
    check_wellformedness_enter as module_check_wellformedness_enter,
    check_wellformedness_visit as module_check_wellformedness_visit,
    check_wellformedness_leave as module_check_wellformedness_leave
)

from ast.moduledecl import (
    check_wellformedness_enter as moduledecl_check_wellformedness_enter,
    check_wellformedness_visit as moduledecl_check_wellformedness_visit,
    check_wellformedness_leave as moduledecl_check_wellformedness_leave
)

from ast.parameterdecllist import ( 
    check_wellformedness_enter as parameterdecllist_check_wellformedness_enter,
    check_wellformedness_visit as parameterdecllist_check_wellformedness_visit,
    check_wellformedness_leave as parameterdecllist_check_wellformedness_leave
)

from ast.payloadtypedecl import ( 
    check_wellformedness_enter as payloadtypedecl_check_wellformedness_enter,
    check_wellformedness_visit as payloadtypedecl_check_wellformedness_visit,
    check_wellformedness_leave as payloadtypedecl_check_wellformedness_leave
)

from ast.roledecllist import ( 
    check_wellformedness_enter as roledecllist_check_wellformedness_enter,
    check_wellformedness_visit as roledecllist_check_wellformedness_visit,
    check_wellformedness_leave as roledecllist_check_wellformedness_leave
)

from ast.globel.globalprotocoldecl import ( 
    get_child as globalprotocoldecl_get_child,
    check_wellformedness_enter as globalprotocoldecl_check_wellformedness_enter,
    check_wellformedness_visit as globalprotocoldecl_check_wellformedness_visit,
    check_wellformedness_leave as globalprotocoldecl_check_wellformedness_leave
)

from ast.globel.globalprotocoldef import ( 
    check_wellformedness_enter as globalprotocoldef_check_wellformedness_enter,
    check_wellformedness_visit as globalprotocoldef_check_wellformedness_visit,
    check_wellformedness_leave as globalprotocoldef_check_wellformedness_leave
)

from ast.globel.globalprotocolblock import ( 
    check_wellformedness_enter as \
        globalprotocolblock_check_wellformedness_enter,
    check_wellformedness_visit as \
        globalprotocolblock_check_wellformedness_visit,
    check_wellformedness_leave as \
        globalprotocolblock_check_wellformedness_leave
)

from ast.globel.globalinteractionsequence import ( 
    check_wellformedness_enter as \
        globalinteractionsequence_check_wellformedness_enter,
    check_wellformedness_visit as \
        globalinteractionsequence_check_wellformedness_visit,
    check_wellformedness_leave as \
        globalinteractionsequence_check_wellformedness_leave
)

from ast.globel.globalmessagetransfer import ( 
    check_wellformedness_enter as \
        globalmessagetransfer_check_wellformedness_enter,
    check_wellformedness_visit as \
        globalmessagetransfer_check_wellformedness_visit,
    check_wellformedness_leave as \
        globalmessagetransfer_check_wellformedness_leave
)

from ast.globel.globalchoice import ( 
    check_wellformedness_enter as globalchoice_check_wellformedness_enter,
    check_wellformedness_visit as globalchoice_check_wellformedness_visit,
    check_wellformedness_leave as globalchoice_check_wellformedness_leave
)

from ast.globel.globalrecursion import ( 
    check_wellformedness_enter as globalrecursion_check_wellformedness_enter,
    check_wellformedness_visit as globalrecursion_check_wellformedness_visit,
    check_wellformedness_leave as globalrecursion_check_wellformedness_leave
)

from ast.globel.globalcontinue import ( 
    check_wellformedness_enter as globalcontinue_check_wellformedness_enter,
    check_wellformedness_visit as globalcontinue_check_wellformedness_visit,
    check_wellformedness_leave as globalcontinue_check_wellformedness_leave
)

from ast.globel.globalparallel import ( 
    check_wellformedness_enter as globalparallel_check_wellformedness_enter,
    check_wellformedness_visit as globalparallel_check_wellformedness_visit,
    check_wellformedness_leave as globalparallel_check_wellformedness_leave
)

from ast.globel.globalinterruptible import ( 
    check_wellformedness_enter as \
        globalinterruptible_check_wellformedness_enter,
    check_wellformedness_visit as \
        globalinterruptible_check_wellformedness_visit,
    check_wellformedness_leave as \
        globalinterruptible_check_wellformedness_leave
)

from ast.globel.globaldo import ( 
    check_wellformedness_enter as globaldo_check_wellformedness_enter,
    check_wellformedness_visit as globaldo_check_wellformedness_visit,
    check_wellformedness_leave as globaldo_check_wellformedness_leave
    #get_projected_member_name as globaldo_get_projected_member_name
)

from visit.projector import Projector as Projector
from visit.reachabilitychecker import ReachabilityChecker


# Implementation is coupled to global protocols
class WellformednessChecker(ContextVisitor):
    rc = RoleCollector() # Here because inconvenient to import in the ast modules
    projector = Projector()

    def __init__(self, context_):
        super(WellformednessChecker, self).__init__(context_)

    # Recursive traversal, although some nodes are visited "early" (before going
    # into the children) e.g. sequencing
    def check_wellformedness(self, node_):
        return self.visit(node_)
    
    """def create_reachability_checker(self, role_):
        context_ = self.get_context().parent  # MODULE
        #context_ = context_.push_globalprotocoldecl(gpd)  # FIXME (local)
        #context_ = context_.push_globalprotocoldef(globalprotocoldecl_get_child(gpd))
        
        # HACK: mangling visible global names in place -- better to remove
        # globals and add to locals?
        for g in context_._visible_globals.keys():
            projectionname = globaldo_get_projected_member_name(g, role_)
            context_ = context_.rename_visible_global(g, projectionname)

        return ReachabilityChecker(context_)"""
    
    def clone(self):
        clone = self.get_context().clone()
        return WellformednessChecker(clone)


    def _enter_module(self, node_):
        module_check_wellformedness_enter(self, node_)

    def _context_visit_module(self, node_):
        return module_check_wellformedness_visit(self, node_)

    def _leave_module(self, node_):
        module_check_wellformedness_leave(self, node_)

    def _enter_moduledecl(self, node_):
        moduledecl_check_wellformedness_enter(self, node_)

    def _context_visit_moduledecl(self, node_):
        return moduledecl_check_wellformedness_visit(self, node_)

    def _leave_moduledecl(self, node_):
        moduledecl_check_wellformedness_leave(self, node_)

    def _enter_importmodule(self, node_):
        importmodule_check_wellformedness_enter(self, node_)

    def _context_visit_importmodule(self, node_):
        return importmodule_check_wellformedness_visit(self, node_)

    def _leave_importmodule(self, node_):
        importmodule_check_wellformedness_leave(self, node_)

    def _enter_payloadtypedecl(self, node_):
        payloadtypedecl_check_wellformedness_enter(self, node_)

    def _context_visit_payloadtypedecl(self, node_):
        return payloadtypedecl_check_wellformedness_visit(self, node_)

    def _leave_payloadtypedecl(self, node_):
        payloadtypedecl_check_wellformedness_leave(self, node_)

    def _enter_roledecllist(self, node_):
        roledecllist_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_roledecllist(node_)

    def _context_visit_roledecllist(self, node_):
        return roledecllist_check_wellformedness_visit(self, node_)

    def _leave_roledecllist(self, node_):
        super(WellformednessChecker, self)._leave_roledecllist(node_)
        roledecllist_check_wellformedness_leave(self, node_)

    def _enter_parameterdecllist(self, node_):
        parameterdecllist_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_parameterdecllist(node_)

    def _context_visit_parameterdecllist(self, node_):
        return parameterdecllist_check_wellformedness_visit(self, node_)

    def _leave_parameterdecllist(self, node_):
        super(WellformednessChecker, self)._leave_parameterdecllist(node_)
        parameterdecllist_check_wellformedness_leave(self, node_)


    # Contract is that the checker should first see the original context, and then
    # we push the new scope
    #
    # Need to check well-formedness first before updating the context state
    #
    # Other ContextVisitor subclasses (run on a later pass after WF checker, and
    # only need to see the result of context building) may do the other way around
    #
    # A better approach may be to record the contexts on the nodes for later passes
    # (Context building vs. visiting)
    #
    # choice, recursion, etc. will follow this pattern
    def _enter_globalprotocoldecl(self, node_):
        globalprotocoldecl_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalprotocoldecl(node_)

    def _context_visit_globalprotocoldecl(self, node_):
        return globalprotocoldecl_check_wellformedness_visit(self, node_)

    def _leave_globalprotocoldecl(self, node_):
        super(WellformednessChecker, self)._leave_globalprotocoldecl(node_)
        globalprotocoldecl_check_wellformedness_leave(self, node_)

    def _enter_globalprotocoldef(self, node_):
        globalprotocoldef_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalprotocoldef(node_)

    def _context_visit_globalprotocoldef(self, node_):
        return globalprotocoldef_check_wellformedness_visit(self, node_)

    def _leave_globalprotocoldef(self, node_):
        super(WellformednessChecker, self)._leave_globalprotocoldef(node_)
        globalprotocoldef_check_wellformedness_leave(self, node_)

    def _enter_globalprotocolblock(self, node_):
        globalprotocolblock_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalprotocolblock(node_)

    def _context_visit_globalprotocolblock(self, node_):
        return globalprotocolblock_check_wellformedness_visit(self, node_)

    def _leave_globalprotocolblock(self, node_):
        super(WellformednessChecker, self)._leave_globalprotocolblock(node_)
        globalprotocolblock_check_wellformedness_leave(self, node_)

    def _enter_globalinteractionsequence(self, node_):
        globalinteractionsequence_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalinteractionsequence(node_)

    def _context_visit_globalinteractionsequence(self, node_):
        return globalinteractionsequence_check_wellformedness_visit(self, node_)

    def _leave_globalinteractionsequence(self, node_):
        super(WellformednessChecker, self)._leave_globalinteractionsequence(node_)
        globalinteractionsequence_check_wellformedness_leave(self, node_)

    def _enter_globalmessagetransfer(self, node_):
        globalmessagetransfer_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalmessagetransfer(node_)

    def _context_visit_globalmessagetransfer(self, node_):
        return globalmessagetransfer_check_wellformedness_visit(self, node_)

    def _leave_globalmessagetransfer(self, node_):
        super(WellformednessChecker, self)._leave_globalmessagetransfer(node_)
        globalmessagetransfer_check_wellformedness_leave(self, node_)

    def _enter_globalchoice(self, node_):
        globalchoice_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalchoice(node_)

    def _context_visit_globalchoice(self, node_):
        return globalchoice_check_wellformedness_visit(self, node_)

    def _leave_globalchoice(self, node_):
        super(WellformednessChecker, self)._leave_globalchoice(node_)
        globalchoice_check_wellformedness_leave(self, node_)

    def _enter_globalrecursion(self, node_):
        globalrecursion_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalrecursion(node_)

    def _context_visit_globalrecursion(self, node_):
        return globalrecursion_check_wellformedness_visit(self, node_)

    def _leave_globalrecursion(self, node_):
        super(WellformednessChecker, self)._leave_globalrecursion(node_)
        globalrecursion_check_wellformedness_leave(self, node_)

    def _enter_globalcontinue(self, node_):
        globalcontinue_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalcontinue(node_)

    def _context_visit_globalcontinue(self, node_):
        return globalcontinue_check_wellformedness_visit(self, node_)

    def _leave_globalcontinue(self, node_):
        super(WellformednessChecker, self)._leave_globalcontinue(node_)
        globalcontinue_check_wellformedness_leave(self, node_)

    def _enter_globalparallel(self, node_):
        globalparallel_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalparallel(node_)

    def _context_visit_globalparallel(self, node_):
        return globalparallel_check_wellformedness_visit(self, node_)

    def _leave_globalparallel(self, node_):
        super(WellformednessChecker, self)._leave_globalparallel(node_)
        globalparallel_check_wellformedness_leave(self, node_)

    def _enter_globalinterruptible(self, node_):
        globalinterruptible_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globalinterruptible(node_)

    def _context_visit_globalinterruptible(self, node_):
        return globalinterruptible_check_wellformedness_visit(self, node_)

    def _leave_globalinterruptible(self, node_):
        super(WellformednessChecker, self)._leave_globalinterruptible(node_)
        globalinterruptible_check_wellformedness_leave(self, node_)

    def _enter_globaldo(self, node_):
        globaldo_check_wellformedness_enter(self, node_)
        super(WellformednessChecker, self)._enter_globaldo(node_)

    def _context_visit_globaldo(self, node_):
        return globaldo_check_wellformedness_visit(self, node_)

    def _leave_globaldo(self, node_):
        super(WellformednessChecker, self)._leave_globaldo(node_)
        globaldo_check_wellformedness_leave(self, node_)
