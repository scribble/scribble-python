# DEPRECATED


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

from ast.globel.localprotocoldecl import (
    context_visitor_enter as localprotocoldecl_context_visitor_enter,
    context_visitor_visit as localprotocoldecl_context_visitor_visit,
    context_visitor_leave as localprotocoldecl_context_visitor_leave
) 

from ast.globel.localmessagetransfer import ( 
    context_visitor_enter as localmessagetransfer_context_visitor_enter,
    context_visitor_visit as localmessagetransfer_context_visitor_visit,
    context_visitor_leave as localmessagetransfer_context_visitor_leave
) 

from ast.globel.localchoice import ( 
    context_visitor_enter as localchoice_context_visitor_enter,
    context_visitor_visit as localchoice_context_visitor_visit,
    context_visitor_leave as localchoice_context_visitor_leave
) 

from ast.globel.localrecursion import ( 
    context_visitor_enter as localrecursion_context_visitor_enter,
    context_visitor_visit as localrecursion_context_visitor_visit,
    context_visitor_leave as localrecursion_context_visitor_leave
) 

from ast.globel.localcontinue import ( 
    context_visitor_enter as localcontinue_context_visitor_enter,
    context_visitor_visit as localcontinue_context_visitor_visit,
    context_visitor_leave as localcontinue_context_visitor_leave
) 

from ast.globel.localparallel import ( 
    context_visitor_enter as localparallel_context_visitor_enter,
    context_visitor_visit as localparallel_context_visitor_visit,
    context_visitor_leave as localparallel_context_visitor_leave
) 

from ast.globel.localinterruptible import ( 
    context_visitor_enter as localinterruptible_context_visitor_enter,
    context_visitor_visit as localinterruptible_context_visitor_visit,
    context_visitor_leave as localinterruptible_context_visitor_leave
) 

from ast.globel.localdo import ( 
    context_visitor_enter as localdo_context_visitor_enter,
    context_visitor_visit as localdo_context_visitor_visit,
    context_visitor_leave as localdo_context_visitor_leave
) 


# TODO: factor out with ContextVisitor
class LocalContextVisitor(Visitor):
    #def __init__(self, importPath, payloadPath):
    def __init__(self, context_):
        super(LocalContextVisitor, self).__init__()
        #Visitor.Visitor.__init__(self)
        self.context = context_

    # Generic ContextVisitor enter/leave that simply uses the default Context
    # push/pop methods. Most constructs will use node-specific routines
    def enter(self, node_):  # Not sure how many places use the generic enter/leave
        context = self.context.push(node_)
        self.context = context

    # Not a simple pop (i.e. simple dual to enter/push, as in
    # AbstractContext.pop) because the Context has been updated: need to keep
    # the new information, but get back the parent/node_ pointers of the parent
    def leave(self, node_):
        self.context = self.context.pop()

    # Getter/setter used by subclasses
    def get_context(self):
        return self.context

    def set_context(self, context):
        self.context = context

    def clone(self):
        raise NotImplementedError("Abstract LocalContextVisitor clone")


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

    def _enter_localprotocoldecl(self, node_):
        localprotocoldecl_context_visitor_enter(self, node_)

    def _context_visit_localprotocoldecl(self, node_):
        return localprotocoldecl_context_visitor_visit(self, node_)

    def _leave_localprotocoldecl(self, node_):
        localprotocoldecl_context_visitor_leave(self, node_)

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

    def _enter_localprotocoldef(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_localprotocoldef(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_localprotocoldef(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_localProtocolBody(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_localProtocolBody(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_localProtocolBody(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_localprotocolblock(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_localprotocolblock(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_localprotocolblock(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_localinteractionsequence(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _context_visit_localinteractionsequence(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        return node_

    def _leave_localinteractionsequence(self, node_):
        #raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_localmessagetransfer(self, node_):
        localmessagetransfer_context_visitor_enter(self, node_)

    def _context_visit_localmessagetransfer(self, node_):
        return localmessagetransfer_context_visitor_visit(self, node_)

    def _leave_localmessagetransfer(self, node_):
        localmessagetransfer_context_visitor_leave(self, node_)

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
    # enter prepares the visitor context
    # leave updates the context after visiting
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

    def _visit_localprotocoldecl(self, node_):
        self._enter_localprotocoldecl(node_)
        new = self._context_visit_localprotocoldecl(node_)
        self._leave_localprotocoldecl(new)
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

    def _visit_localmessagetransfer(self, node_):
        self._enter_localmessagetransfer(node_)
        new = self._context_visit_localmessagetransfer(node_)
        self._leave_localmessagetransfer(new)
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
