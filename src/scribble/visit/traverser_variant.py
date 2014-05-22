

# DEPRECATED


# HACK: variation of traverser which visits the node after traversing its
# child, instead of before


import scrib_constants as constants
import scrib_util as util

from visit.visitor import Visitor as Visitor

from ast.importmodule import traverse as importmodule_traverse 
# TODO: import members
from ast.module import traverse as module_traverse
from ast.moduledecl import traverse as moduledecl_traverse
from ast.parameterdecllist import traverse as parameterdecllist_traverse
from ast.payloadtypedecl import traverse as payloadtypedecl_traverse
from ast.roledecllist import traverse as roledecllist_traverse
from ast.roleinstantiationlist import \
    traverse as roleinstantiationlist_traverse
from ast.roleinstantiation import traverse as roleinstantiation_traverse
from ast.argumentlist import traverse as argumentlist_traverse
from ast.argument import traverse as argument_traverse
from ast.messagesignature import traverse as messagesignature_traverse
from ast.payload import traverse as payload_traverse
from ast.payloadelement import traverse as payloadelement_traverse

from ast.globel.globalprotocoldecl import \
    traverse as globalprotocoldecl_traverse
from ast.globel.globalprotocoldef import \
    traverse as globalprotocoldef_traverse
from ast.globel.globalprotocolblock import \
    traverse as globalprotocolblock_traverse
from ast.globel.globalinteractionsequence import \
    traverse as globalinteractionsequence_traverse
from ast.globel.globalmessagetransfer import \
    traverse as globalmessagetransfer_traverse
from ast.globel.globalchoice import traverse as globalchoice_traverse
from ast.globel.globalrecursion import traverse as globalrecursion_traverse
from ast.globel.globalcontinue import traverse as globalcontinue_traverse
from ast.globel.globalparallel import traverse as globalparallel_traverse
from ast.globel.globalinterruptible import \
    traverse as globalinterruptible_traverse
from ast.globel.globalinterrupt import traverse as globalinterrupt_traverse
from ast.globel.globaldo import traverse as globaldo_traverse

from ast.local.localprotocoldecl import \
    traverse as localprotocoldecl_traverse
from ast.local.localprotocoldef import \
    traverse as localprotocoldef_traverse
from ast.local.localprotocolblock import \
    traverse as localprotocolblock_traverse
from ast.local.localinteractionsequence import \
    traverse as localinteractionsequence_traverse
from ast.local.localsend import traverse as localsend_traverse
from ast.local.localreceive import traverse as localreceive_traverse
from ast.local.localchoice import traverse as localchoice_traverse
from ast.local.localrecursion import traverse as localrecursion_traverse
from ast.local.localcontinue import traverse as localcontinue_traverse
from ast.local.localparallel import traverse as localparallel_traverse
from ast.local.localinterruptible import \
    traverse as localinterruptible_traverse
from ast.local.localthrow import traverse as localthrow_traverse
from ast.local.localcatch import traverse as localcatch_traverse
from ast.local.localdo import traverse as localdo_traverse


# Not integrated with ContextVisitor (enter/exit node pattern) for a single AST
# Visitor pattern (both enter/exit and graph (children) traversal)  --
# ContextVisitor needs to access the separate contexts from each visited
# (traversed) child, which the generic traverse routine doesn't support well --
# and traverse doesn't need enter/exit structure, no context to be maintained
class Traverser(Visitor):
    def __init__(self):
        super(Traverser, self).__init__()


    # Traverse "typed" AST nodes (type is the getText label); cf. traverse_untyped_leaf
    def traverse(self, node_):
        return self.visit(node_)

    """# For "untyped" nodes, where node_.getText() is the value, e.g. role names,
    # parameter names, etc.
    def traverse_untyped_leaf(self, node_):
        return self.visit_untyped_leaf(node_)"""


    ##
    # Delegate enter/visit/leave procedures to appropriate modules

    def _enter_module(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_module(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_moduledecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_moduledecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))
        pass

    def _enter_payloadtypedecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_payloadtypedecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_roledecllist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_roledecllist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_parameterdecllist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_parameterdecllist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))


    def _enter_globalprotocoldecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalprotocoldecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalprotocoldef(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalprotocoldef(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalprotocolblock(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalprotocolblock(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalinteractionsequence(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalinteractionsequence(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalmessagetransfer(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalmessagetransfer(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalchoice(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalchoice(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalrecursion(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalrecursion(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalcontinue(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalcontinue(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalparallel(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalparallel(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalinterruptible(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalinterruptible(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globalinterrupt(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globalinterrupt(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _enter_globaldo(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _leave_globaldo(self, node_):
        raise NotImplementedError(util.get_node_type(node_))
        
        
    ##
    # Enter/visit/leave pattern. 
    # enter prepares the visitor _context
    # leave updates the _context after visiting
    # visit returns the visited node
    # enter/leave have void return (self-setting the Context)

    def _visit_module(self, node_):
        self._enter_module(node_)
        new = self._traverse_module(node_)
        self._leave_module(new)
        return new

    def _visit_moduledecl(self, node_):
        self._enter_moduledecl(node_)
        new = self._traverse_moduledecl(node_)
        self._leave_moduledecl(new)
        return new

    def _visit_importmodule(self, node_):
        self._enter_importmodule(node_)
        new = self._traverse_importmodule(node_)
        self._leave_importmodule(new)
        return new

    def _visit_payloadtypedecl(self, node_):
        self._enter_payloadtypedecl(node_)
        new = self._traverse_payloadtypedecl(node_)
        self._leave_payloadtypedecl(new)
        return new

    def _visit_roledecllist(self, node_):
        self._enter_roledecllist(node_)
        new = self._traverse_roledecllist(node_)
        self._leave_roledecllist(new)
        return new

    def _visit_parameterdecllist(self, node_):
        self._enter_parameterdecllist(node_)
        new = self._traverse_parameterdecllist(node_)
        self._leave_parameterdecllist(new)
        return new


    def _visit_globalprotocoldecl(self, node_):
        self._enter_globalprotocoldecl(node_)
        new = self._traverse_globalprotocoldecl(node_)
        self._leave_globalprotocoldecl(new)
        return new

    def _visit_globalprotocoldef(self, node_):
        self._enter_globalprotocoldef(node_)
        new = self._traverse_globalprotocoldef(node_)
        self._leave_globalprotocoldef(new)
        return new

    def _visit_globalprotocolblock(self, node_):
        self._enter_globalprotocolblock(node_)
        new = self._traverse_globalprotocolblock(node_)
        self._leave_globalprotocolblock(new)
        return new

    def _visit_globalinteractionsequence(self, node_):
        self._enter_globalinteractionsequence(node_)
        new = self._traverse_globalinteractionsequence(node_)
        self._leave_globalinteractionsequence(new)
        return new

    def _visit_globalmessagetransfer(self, node_):
        self._enter_globalmessagetransfer(node_)
        new = self._traverse_globalmessagetransfer(node_)
        self._leave_globalmessagetransfer(new)
        return new

    def _visit_globalchoice(self, node_):
        self._enter_globalchoice(node_)
        new = self._traverse_globalchoice(node_)
        self._leave_globalchoice(new)
        return new

    def _visit_globalrecursion(self, node_):
        self._enter_globalrecursion(node_)
        new = self._traverse_globalrecursion(node_)
        self._leave_globalrecursion(new)
        return new

    def _visit_globalcontinue(self, node_):
        self._enter_globalcontinue(node_)
        new = self._traverse_globalcontinue(node_)
        self._leave_globalcontinue(new)
        return new

    def _visit_globalparallel(self, node_):
        self._enter_globalparallel(node_)
        new = self._traverse_globalparallel(node_)
        self._leave_globalparallel(new)
        return new

    def _visit_globalinterruptible(self, node_):
        self._enter_globalinterruptible(node_)
        new = self._traverse_globalinterruptible(node_)
        self._leave_globalinterruptible(new)
        return new

    def _visit_globalinterrupt(self, node_):
        self._enter_globalinterrupt(node_)
        new = self._traverse_globalinterrupt(node_)
        self._leave_globalinterrupt(new)
        return new

    def _visit_globaldo(self, node_):
        self._enter_globaldo(node_)
        new = self._traverse_globaldo(node_)
        self._leave_globaldo(new)
        return new


    def _traverse_module(self, node_):
        return module_traverse(self, node_)

    def _traverse_moduledecl(self, node_):
        return moduledecl_traverse(self, node_)

    def _traverse_importmodule(self, node_):
        return importmodule_traverse(self, node_)

    def _traverse_payloadtypedecl(self, node_):
        return payloadtypedecl_traverse(self, node_)

    def _traverse_globalprotocoldecl(self, node_):
        return globalprotocoldecl_traverse(self, node_)

    def _traverse_roledecllist(self, node_):
        return roledecllist_traverse(self, node_)

    def _traverse_parameterdecllist(self, node_):
        return parameterdecllist_traverse(self, node_)

    def _traverse_globalprotocoldef(self, node_):
        return globalprotocoldef_traverse(self, node_)

    def _traverse_roleinstantiationlist(self, node_):
        return roleinstantiationlist_traverse(self, node_)

    def _traverse_roleinstantiation(self, node_):
        return roleinstantiation_traverse(self, node_)

    def _traverse_argumentlist(self, node_):
        return argumentlist_traverse(self, node_)

    def _traverse_argument(self, node_):
        return argument_traverse(self, node_)

    def _traverse_globalprotocolblock(self, node_):
        return globalprotocolblock_traverse(self, node_)

    def _traverse_globalinteractionsequence(self, node_):
        return globalinteractionsequence_traverse(self, node_)

    def _traverse_globalmessagetransfer(self, node_):
        return globalmessagetransfer_traverse(self, node_)

    def _traverse_messagesignature(self, node_):
        return messagesignature_traverse(self, node_)

    def _traverse_payload(self, node_):
        return payload_traverse(self, node_)

    def _traverse_payloadelement(self, node_):
        return payloadelement_traverse(self, node_)

    def _traverse_globalchoice(self, node_):
        return globalchoice_traverse(self, node_)

    def _traverse_globalrecursion(self, node_):
        return globalrecursion_traverse(self, node_)

    def _traverse_globalcontinue(self, node_):
        return globalcontinue_traverse(self, node_)

    def _traverse_globalparallel(self, node_):
        return globalparallel_traverse(self, node_)

    def _traverse_globalinterruptible(self, node_):
        return globalinterruptible_traverse(self, node_)

    def _traverse_globalinterrupt(self, node_):
        return globalinterrupt_traverse(self, node_)

    def _traverse_globaldo(self, node_):
        return globaldo_traverse(self, node_)

    def _traverse_localprotocoldecl(self, node_):
        return localprotocoldecl_traverse(self, node_)

    def _traverse_roledecllist(self, node_):
        return roledecllist_traverse(self, node_)

    def _traverse_parameterdecllist(self, node_):
        return parameterdecllist_traverse(self, node_)

    def _traverse_localprotocoldef(self, node_):
        return localprotocoldef_traverse(self, node_)

    def _traverse_localprotocolblock(self, node_):
        return localprotocolblock_traverse(self, node_)

    def _traverse_localinteractionsequence(self, node_):
        return localinteractionsequence_traverse(self, node_)

    def _traverse_localsend(self, node_):
        return localsend_traverse(self, node_)

    def _traverse_localreceive(self, node_):
        return localreceive_traverse(self, node_)

    def _traverse_localchoice(self, node_):
        return localchoice_traverse(self, node_)

    def _traverse_localrecursion(self, node_):
        return localrecursion_traverse(self, node_)

    def _traverse_localcontinue(self, node_):
        return localcontinue_traverse(self, node_)

    def _traverse_localparallel(self, node_):
        return localparallel_traverse(self, node_)

    def _traverse_localinterruptible(self, node_):
        return localinterruptible_traverse(self, node_)

    def _traverse_localthrow(self, node_):
        return localthrow_traverse(self, node_)

    def _traverse_localcatch(self, node_):
        return localcatch_traverse(self, node_)

    def _traverse_localdo(self, node_):
        return localdo_traverse(self, node_)
