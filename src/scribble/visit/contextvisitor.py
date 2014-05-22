import scrib_util as util

from visit.context import Context as Context
from visit.visitor import Visitor as Visitor

# The following are the AST nodes that use the ContextVisitor enter/visit/leave
# pattern; other nodes are passed over (they don't affect Context contents)

from ast.roledecllist import (
    context_visitor_enter as roledecllist_context_visitor_enter,
    context_visitor_visit as roledecllist_context_visitor_visit,
    context_visitor_leave as roledecllist_context_visitor_leave
) 

from ast.parameterdecllist import (
    context_visitor_enter as parameterdecllist_context_visitor_enter,
    context_visitor_visit as parameterdecllist_context_visitor_visit,
    context_visitor_leave as parameterdecllist_context_visitor_leave
)

from ast.globel.globalprotocoldecl import (
    context_visitor_enter as globalprotocoldecl_context_visitor_enter,
    context_visitor_visit as globalprotocoldecl_context_visitor_visit,
    context_visitor_leave as globalprotocoldecl_context_visitor_leave
) 

from ast.globel.globalprotocoldef import (
    context_visitor_enter as globalprotocoldef_context_visitor_enter,
    context_visitor_visit as globalprotocoldef_context_visitor_visit,
    context_visitor_leave as globalprotocoldef_context_visitor_leave
) 

from ast.globel.globalprotocolblock import (
    context_visitor_enter as globalprotocolblock_context_visitor_enter,
    context_visitor_visit as globalprotocolblock_context_visitor_visit,
    context_visitor_leave as globalprotocolblock_context_visitor_leave
) 

from ast.globel.globalinteractionsequence import (
    context_visitor_enter as globalinteractionsequence_context_visitor_enter,
    context_visitor_visit as globalinteractionsequence_context_visitor_visit,
    context_visitor_leave as globalinteractionsequence_context_visitor_leave
) 

from ast.globel.globalmessagetransfer import ( 
    context_visitor_enter as globalmessagetransfer_context_visitor_enter,
    context_visitor_visit as globalmessagetransfer_context_visitor_visit,
    context_visitor_leave as globalmessagetransfer_context_visitor_leave
) 

from ast.globel.globalchoice import ( 
    context_visitor_enter as globalchoice_context_visitor_enter,
    context_visitor_visit as globalchoice_context_visitor_visit,
    context_visitor_leave as globalchoice_context_visitor_leave
) 

from ast.globel.globalrecursion import ( 
    context_visitor_enter as globalrecursion_context_visitor_enter,
    context_visitor_visit as globalrecursion_context_visitor_visit,
    context_visitor_leave as globalrecursion_context_visitor_leave
) 

from ast.globel.globalcontinue import ( 
    context_visitor_enter as globalcontinue_context_visitor_enter,
    context_visitor_visit as globalcontinue_context_visitor_visit,
    context_visitor_leave as globalcontinue_context_visitor_leave
) 

from ast.globel.globalparallel import ( 
    context_visitor_enter as globalparallel_context_visitor_enter,
    context_visitor_visit as globalparallel_context_visitor_visit,
    context_visitor_leave as globalparallel_context_visitor_leave
) 

from ast.globel.globalinterruptible import ( 
    context_visitor_enter as globalinterruptible_context_visitor_enter,
    context_visitor_visit as globalinterruptible_context_visitor_visit,
    context_visitor_leave as globalinterruptible_context_visitor_leave
) 

from ast.globel.globaldo import ( 
    context_visitor_enter as globaldo_context_visitor_enter,
    context_visitor_visit as globaldo_context_visitor_visit,
    context_visitor_leave as globaldo_context_visitor_leave
) 


# Implementation is coupled to global protocols
class ContextVisitor(Visitor):
    #def __init__(self, importPath, payloadPath):
    def __init__(self, context_):
        super(ContextVisitor, self).__init__()
        #Visitor.Visitor.__init__(self)
        self._context = context_

    # Generic ContextVisitor enter/leave that simply uses the default Context
    # push/pop methods. Most constructs will use node-specific routines
    def enter(self, node_):  # Not sure how many places use the generic enter/leave
        context = self._context.push(node_)
        self._context = context

    # Not a simple pop (i.e. simple dual to enter/push, as in
    # AbstractContext.pop) because the Context has been updated: need to keep
    # the new information, but get back the parent/node_ pointers of the parent
    def leave(self, node_):
        self._context = self._context.pop()

    # Getter/setter used by subclasses
    def get_context(self):
        return self._context

    def set_context(self, context):
        self._context = context

    def clone(self):
        raise NotImplementedError("Abstract ContextVisitor clone")


    ##
    # Delegate enter/visit/leave procedures to appropriate modules

    def _enter_module(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_module(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_module(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_moduledecl(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_moduledecl(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_moduledecl(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_payloadtypedecl(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_payloadtypedecl(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_payloadtypedecl(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_roledecllist(self, node_):
        roledecllist_context_visitor_enter(self, node_)

    def _context_visit_roledecllist(self, node_):
        return roledecllist_context_visitor_visit(self, node_)

    def _leave_roledecllist(self, node_):
        roledecllist_context_visitor_leave(self, node_)

    def _enter_parameterdecllist(self, node_):
        parameterdecllist_context_visitor_enter(self, node_)

    def _context_visit_parameterdecllist(self, node_):
        return parameterdecllist_context_visitor_visit(self, node_)

    def _leave_parameterdecllist(self, node_):
        parameterdecllist_context_visitor_leave(self, node_)


    def _enter_globalprotocoldecl(self, node_):
        globalprotocoldecl_context_visitor_enter(self, node_)

    def _context_visit_globalprotocoldecl(self, node_):
        return globalprotocoldecl_context_visitor_visit(self, node_)

    def _leave_globalprotocoldecl(self, node_):
        globalprotocoldecl_context_visitor_leave(self, node_)

    def _enter_globalprotocoldef(self, node_):
        globalprotocoldef_context_visitor_enter(self, node_)

    def _context_visit_globalprotocoldef(self, node_):
        return globalprotocoldef_context_visitor_visit(self, node_)

    def _leave_globalprotocoldef(self, node_):
        globalprotocoldef_context_visitor_leave(self, node_)

    def _enter_globalprotocolblock(self, node_):
        globalprotocolblock_context_visitor_enter(self, node_)

    def _context_visit_globalprotocolblock(self, node_):
        return globalprotocolblock_context_visitor_visit(self, node_)

    def _leave_globalprotocolblock(self, node_):
        globalprotocolblock_context_visitor_leave(self, node_)

    def _enter_globalinteractionsequence(self, node_):
        globalinteractionsequence_context_visitor_enter(self, node_)

    def _context_visit_globalinteractionsequence(self, node_):
        return globalinteractionsequence_context_visitor_visit(self, node_)

    def _leave_globalinteractionsequence(self, node_):
        globalinteractionsequence_context_visitor_leave(self, node_)

    def _enter_globalmessagetransfer(self, node_):
        globalmessagetransfer_context_visitor_enter(self, node_)

    def _context_visit_globalmessagetransfer(self, node_):
        return globalmessagetransfer_context_visitor_visit(self, node_)

    def _leave_globalmessagetransfer(self, node_):
        globalmessagetransfer_context_visitor_leave(self, node_)

    def _enter_globalchoice(self, node_):
        globalchoice_context_visitor_enter(self, node_)

    def _context_visit_globalchoice(self, node_):
        return globalchoice_context_visitor_visit(self, node_)

    def _leave_globalchoice(self, node_):
        globalchoice_context_visitor_leave(self, node_)

    def _enter_globalrecursion(self, node_):
        globalrecursion_context_visitor_enter(self, node_)

    def _context_visit_globalrecursion(self, node_):
        return globalrecursion_context_visitor_visit(self, node_)

    def _leave_globalrecursion(self, node_):
        globalrecursion_context_visitor_leave(self, node_)

    def _enter_globalcontinue(self, node_):
        globalcontinue_context_visitor_enter(self, node_)

    def _context_visit_globalcontinue(self, node_):
        return globalcontinue_context_visitor_continue(self, node_)

    def _leave_globalcontinue(self, node_):
        globalcontinue_context_visitor_leave(self, node_)

    def _enter_globalparallel(self, node_):
        globalparallel_context_visitor_enter(self, node_)

    def _context_visit_globalparallel(self, node_):
        return globalparallel_context_visitor_visit(self, node_)

    def _leave_globalparallel(self, node_):
        globalparallel_context_visitor_leave(self, node_)

    def _enter_globalinterruptible(self, node_):
        globalinterruptible_context_visitor_enter(self, node_)

    def _context_visit_globalinterruptible(self, node_):
        return globalinterruptible_context_visitor_visit(self, node_)

    def _leave_globalinterruptible(self, node_):
        globalinterruptible_context_visitor_leave(self, node_)

    def _enter_globalinterrupt(self, node_):
        #raise NotImplementedError(util_get_node_type(node_))
        pass

    def _context_visit_globalinterrupt(self, node_):
        #raise NotImplementedError(util_get_node_type(node_))
        return node_

    def _leave_globalinterrupt(self, node_):
        #raise NotImplementedError(util_get_node_type(node_))
        pass

    def _enter_globaldo(self, node_):
        globaldo_context_visitor_enter(self, node_)

    def _context_visit_globaldo(self, node_):
        return globaldo_context_visitor_visit(self, node_)

    def _leave_globaldo(self, node_):
        globaldo_context_visitor_leave(self, node_)
        
        
    def _enter_localprotocoldecl(self, node_):
        localprotocoldecl_context_visitor_enter(self, node_)

    def _context_visit_localprotocoldecl(self, node_):
        return localprotocoldecl_context_visitor_visit(self, node_)

    def _leave_localprotocoldecl(self, node_):
        localprotocoldecl_context_visitor_leave(self, node_)

    def _enter_localprotocoldef(self, node_):
        localprotocoldef_context_visitor_enter(self, node_)

    def _context_visit_localprotocoldef(self, node_):
        return localprotocoldef_context_visitor_visit(self, node_)

    def _leave_localprotocoldef(self, node_):
        localprotocoldef_context_visitor_leave(self, node_)

    def _enter_localprotocolblock(self, node_):
        localprotocolblock_context_visitor_enter(self, node_)

    def _context_visit_localprotocolblock(self, node_):
        return localprotocolblock_context_visitor_visit(self, node_)

    def _leave_localprotocolblock(self, node_):
        localprotocolblock_context_visitor_leave(self, node_)

    def _enter_localinteractionsequence(self, node_):
        localinteractionsequence_context_visitor_enter(self, node_)

    def _context_visit_localinteractionsequence(self, node_):
        return localinteractionsequence_context_visitor_visit(self, node_)

    def _leave_localinteractionsequence(self, node_):
        localinteractionsequence_context_visitor_leave(self, node_)

    def _enter_localsend(self, node_):
        localsend_context_visitor_enter(self, node_)

    def _context_visit_localsend(self, node_):
        return localsend_context_visitor_visit(self, node_)

    def _leave_localsend(self, node_):
        localsend_context_visitor_leave(self, node_)

    def _enter_localreceive(self, node_):
        localreceive_context_visitor_enter(self, node_)

    def _context_visit_localreceive(self, node_):
        return localreceive_context_visitor_visit(self, node_)

    def _leave_localreceive(self, node_):
        localreceive_context_visitor_leave(self, node_)

    def _enter_localchoice(self, node_):
        localchoice_context_visitor_enter(self, node_)

    def _context_visit_localchoice(self, node_):
        return localchoice_context_visitor_visit(self, node_)

    def _leave_localchoice(self, node_):
        localchoice_context_visitor_leave(self, node_)

    def _enter_localrecursion(self, node_):
        localrecursion_context_visitor_enter(self, node_)

    def _context_visit_localrecursion(self, node_):
        return localrecursion_context_visitor_visit(self, node_)

    def _leave_localrecursion(self, node_):
        localrecursion_context_visitor_leave(self, node_)

    def _enter_localcontinue(self, node_):
        localcontinue_context_visitor_enter(self, node_)

    def _context_visit_localcontinue(self, node_):
        return localcontinue_context_visitor_continue(self, node_)

    def _leave_localcontinue(self, node_):
        localcontinue_context_visitor_leave(self, node_)

    def _enter_localparallel(self, node_):
        localparallel_context_visitor_enter(self, node_)

    def _context_visit_localparallel(self, node_):
        return localparallel_context_visitor_visit(self, node_)

    def _leave_localparallel(self, node_):
        localparallel_context_visitor_leave(self, node_)

    def _enter_localinterruptible(self, node_):
        localinterruptible_context_visitor_enter(self, node_)

    def _context_visit_localinterruptible(self, node_):
        return localinterruptible_context_visitor_visit(self, node_)

    def _leave_localinterruptible(self, node_):
        localinterruptible_context_visitor_leave(self, node_)

    def _enter_localinterrupt(self, node_):
        #raise NotImplementedError(util_get_node_type(node_))
        pass

    def _context_visit_localinterrupt(self, node_):
        #raise NotImplementedError(util_get_node_type(node_))
        return node_

    def _leave_localinterrupt(self, node_):
        #raise NotImplementedError(util_get_node_type(node_))
        pass

    def _enter_localdo(self, node_):
        localdo_context_visitor_enter(self, node_)

    def _context_visit_localdo(self, node_):
        return localdo_context_visitor_visit(self, node_)

    def _leave_localdo(self, node_):
        localdo_context_visitor_leave(self, node_)
        
        
    ##
    # Enter/visit/leave pattern. 
    # enter prepares the visitor _context
    # leave updates the _context after visiting
    # visit returns the visited node
    # enter/leave have void return (self-setting the Context)

    def _visit_module(self, node_):
        self._enter_module(node_)
        new = self._context_visit_module(node_)
        self._leave_module(new)
        return new

    def _visit_moduledecl(self, node_):
        self._enter_moduledecl(node_)
        new = self._context_visit_moduledecl(node_)
        self._leave_moduledecl(new)
        return new

    def _visit_importmodule(self, node_):
        self._enter_importmodule(node_)
        new = self._context_visit_importmodule(node_)
        self._leave_importmodule(new)
        return new

    def _visit_payloadtypedecl(self, node_):
        self._enter_payloadtypedecl(node_)
        new = self._context_visit_payloadtypedecl(node_)
        self._leave_payloadtypedecl(new)
        return new

    def _visit_roledecllist(self, node_):
        self._enter_roledecllist(node_)
        new = self._context_visit_roledecllist(node_)
        self._leave_roledecllist(new)
        return new

    def _visit_parameterdecllist(self, node_):
        self._enter_parameterdecllist(node_)
        new = self._context_visit_parameterdecllist(node_)
        self._leave_parameterdecllist(new)
        return new


    def _visit_globalprotocoldecl(self, node_):
        self._enter_globalprotocoldecl(node_)
        new = self._context_visit_globalprotocoldecl(node_)
        self._leave_globalprotocoldecl(new)
        return new

    def _visit_globalprotocoldef(self, node_):
        self._enter_globalprotocoldef(node_)
        new = self._context_visit_globalprotocoldef(node_)
        self._leave_globalprotocoldef(new)
        return new

    def _visit_globalprotocolblock(self, node_):
        self._enter_globalprotocolblock(node_)
        new = self._context_visit_globalprotocolblock(node_)
        self._leave_globalprotocolblock(new)
        return new

    def _visit_globalinteractionsequence(self, node_):
        self._enter_globalinteractionsequence(node_)
        new = self._context_visit_globalinteractionsequence(node_)
        self._leave_globalinteractionsequence(new)
        return new

    def _visit_globalmessagetransfer(self, node_):
        self._enter_globalmessagetransfer(node_)
        new = self._context_visit_globalmessagetransfer(node_)
        self._leave_globalmessagetransfer(new)
        return new

    def _visit_globalchoice(self, node_):
        self._enter_globalchoice(node_)
        new = self._context_visit_globalchoice(node_)
        self._leave_globalchoice(new)
        return new

    def _visit_globalrecursion(self, node_):
        self._enter_globalrecursion(node_)
        new = self._context_visit_globalrecursion(node_)
        self._leave_globalrecursion(new)
        return new

    def _visit_globalcontinue(self, node_):
        self._enter_globalcontinue(node_)
        new = self._context_visit_globalcontinue(node_)
        self._leave_globalcontinue(new)
        return new

    def _visit_globalparallel(self, node_):
        self._enter_globalparallel(node_)
        new = self._context_visit_globalparallel(node_)
        self._leave_globalparallel(new)
        return new

    def _visit_globalinterruptible(self, node_):
        self._enter_globalinterruptible(node_)
        new = self._context_visit_globalinterruptible(node_)
        self._leave_globalinterruptible(new)
        return new

    def _visit_globalinterrupt(self, node_):
        self._enter_globalinterrupt(node_)
        new = self._context_visit_globalinterrupt(node_)
        self._leave_globalinterrupt(new)
        return new

    def _visit_globaldo(self, node_):
        self._enter_globaldo(node_)
        new = self._context_visit_globaldo(node_)
        self._leave_globaldo(new)
        return new


    # For ANTLR parsed protocols, not NodeFactory constructed (projections)

    def _visit_localprotocoldecl(self, node_):
        self._enter_localprotocoldecl(node_)
        new = self._context_visit_localprotocoldecl(node_)
        self._leave_localprotocoldecl(new)
        return new

    def _visit_localprotocoldef(self, node_):
        self._enter_localprotocoldef(node_)
        new = self._context_visit_localprotocoldef(node_)
        self._leave_localprotocoldef(new)
        return new

    def _visit_localprotocolblock(self, node_):
        self._enter_localprotocolblock(node_)
        new = self._context_visit_localprotocolblock(node_)
        self._leave_localprotocolblock(new)
        return new

    def _visit_localinteractionsequence(self, node_):
        self._enter_localinteractionsequence(node_)
        new = self._context_visit_localinteractionsequence(node_)
        self._leave_localinteractionsequence(new)
        return new

    def _visit_localsend(self, node_):
        self._enter_localsend(node_)
        new = self._context_visit_localsend(node_)
        self._leave_localsend(new)
        return new

    def _visit_localreceive(self, node_):
        self._enter_localreceive(node_)
        new = self._context_visit_localreceive(node_)
        self._leave_localreceive(new)
        return new

    def _visit_localchoice(self, node_):
        self._enter_localchoice(node_)
        new = self._context_visit_localchoice(node_)
        self._leave_localchoice(new)
        return new

    def _visit_localrecursion(self, node_):
        self._enter_localrecursion(node_)
        new = self._context_visit_localrecursion(node_)
        self._leave_localrecursion(new)
        return new

    def _visit_localcontinue(self, node_):
        self._enter_localcontinue(node_)
        new = self._context_visit_localcontinue(node_)
        self._leave_localcontinue(new)
        return new

    def _visit_localparallel(self, node_):
        self._enter_localparallel(node_)
        new = self._context_visit_localparallel(node_)
        self._leave_localparallel(new)
        return new

    def _visit_localinterruptible(self, node_):
        self._enter_localinterruptible(node_)
        new = self._context_visit_localinterruptible(node_)
        self._leave_localinterruptible(new)
        return new

    def _visit_localinterrupt(self, node_):
        self._enter_localinterrupt(node_)
        new = self._context_visit_localinterrupt(node_)
        self._leave_localinterrupt(new)
        return new

    def _visit_localdo(self, node_):
        self._enter_localdo(node_)
        new = self._context_visit_localdo(node_)
        self._leave_localdo(new)
        return new
