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
    def traverse(self, visited):
        # Visit current node first, then traverse children
        visited = self.visit(visited)

        ntype = util.get_node_type(visited)
        # Same structure as Visitor (no argument overloading...)
        if ntype == constants.MODULE_NODE_TYPE:
            return self._traverse_module(visited)
        elif ntype == constants.MODULE_DECL_NODE_TYPE:
            return self._traverse_moduledecl(visited)
        #elif ntype == constants.IMPORT_DECL_NODE_TYPE:
        #    return self._traverse_ImportDecl(visited)
        elif ntype == constants.IMPORT_MODULE_NODE_TYPE:  # FIXME: also members
            return self._traverse_importmodule(visited)
        elif ntype == constants.PAYLOAD_DECL_NODE_TYPE:
            return self._traverse_payloadtypedecl(visited)
        elif ntype == constants.GLOBAL_PROTOCOL_DECL_NODE_TYPE:
            return self._traverse_globalprotocoldecl(visited)
        elif ntype == constants.ROLE_DECL_LIST_NODE_TYPE:
            return self._traverse_roledecllist(visited)
        elif ntype == constants.ROLE_DECL_NODE_TYPE:
            return self._traverse_roledecl(visited)
        elif ntype == constants.PARAMETER_DECL_LIST_NODE_TYPE:
            return self._traverse_parameterdecllist(visited)
        elif ntype == constants.PARAMETER_DECL_NODE_TYPE:
            return self._traverse_parameterdecl(visited)
        elif ntype == constants.GLOBAL_PROTOCOL_DEF_NODE_TYPE:
            return self._traverse_globalprotocoldef(visited)
        elif ntype == constants.ROLE_INSTANTIATION_LIST_NODE_TYPE:
            return self._traverse_roleinstantiationlist(visited)
        elif ntype == constants.ROLE_INSTANTIATION_NODE_TYPE:
            return self._traverse_roleinstantiation(visited)
        elif ntype == constants.ARGUMENT_LIST_NODE_TYPE:
            return self._traverse_argumentlist(visited)
        elif ntype == constants.ARGUMENT_NODE_TYPE:
            return self._traverse_argument(visited)
        elif ntype == constants.GLOBAL_PROTOCOL_BLOCK_NODE_TYPE:
            return self._traverse_globalprotocolblock(visited)
        elif ntype == constants.GLOBAL_INTERACTION_SEQUENCE_NODE_TYPE:
            return self._traverse_globalinteractionsequence(visited)
        elif ntype == constants.GLOBAL_MESSAGE_TRANSFER_NODE_TYPE:
            return self._traverse_globalmessagetransfer(visited)
        elif ntype == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            return self._traverse_messagesignature(visited)
        elif ntype == constants.PAYLOAD_NODE_TYPE:
            return self._traverse_payload(visited)
        elif ntype == constants.PAYLOAD_ELEMENT_NODE_TYPE:
            return self._traverse_payloadelement(visited)
        elif ntype == constants.GLOBAL_CHOICE_NODE_TYPE:
            return self._traverse_globalchoice(visited)
        elif ntype == constants.GLOBAL_RECURSION_NODE_TYPE:
            return self._traverse_globalrecursion(visited)
        elif ntype == constants.GLOBAL_CONTINUE_NODE_TYPE:
            return self._traverse_globalcontinue(visited)
        elif ntype == constants.GLOBAL_PARALLEL_NODE_TYPE:
            return self._traverse_globalparallel(visited)
        elif ntype == constants.GLOBAL_INTERRUPTIBLE_NODE_TYPE:
            return self._traverse_globalinterruptible(visited)
        elif ntype == constants.GLOBAL_INTERRUPT_NODE_TYPE:
            return self._traverse_globalinterrupt(visited)
        elif ntype == constants.GLOBAL_DO_NODE_TYPE:
            return self._traverse_globaldo(visited)
        elif ntype == constants.LOCAL_PROTOCOL_DECL_NODE_TYPE:
            return self._traverse_localprotocoldecl(visited)
        elif ntype == constants.LOCAL_PROTOCOL_DEF_NODE_TYPE:
            return self._traverse_localprotocoldef(visited)
        elif ntype == constants.LOCAL_PROTOCOL_BLOCK_NODE_TYPE:
            return self._traverse_localprotocolblock(visited)
        elif ntype == constants.LOCAL_INTERACTION_SEQUENCE_NODE_TYPE:
            return self._traverse_localinteractionsequence(visited)
        elif ntype == constants.LOCAL_SEND_NODE_TYPE:
            return self._traverse_localsend(visited)
        elif ntype == constants.LOCAL_RECEIVE_NODE_TYPE:
            return self._traverse_localreceive(visited)
        elif ntype == constants.LOCAL_CHOICE_NODE_TYPE:
            return self._traverse_localchoice(visited)
        elif ntype == constants.LOCAL_RECURSION_NODE_TYPE:
            return self._traverse_localrecursion(visited)
        elif ntype == constants.LOCAL_CONTINUE_NODE_TYPE:
            return self._traverse_localcontinue(visited)
        elif ntype == constants.LOCAL_PARALLEL_NODE_TYPE:
            return self._traverse_localparallel(visited)
        elif ntype == constants.LOCAL_INTERRUPTIBLE_NODE_TYPE:
            return self._traverse_localinterruptible(visited)
        elif ntype == constants.LOCAL_THROW_NODE_TYPE:
            return self._traverse_localthrow(visited)
        elif ntype == constants.LOCAL_CATCH_NODE_TYPE:
            return self._traverse_localcatch(visited)
        elif ntype == constants.LOCAL_DO_NODE_TYPE:
            return self._traverse_localdo(visited)
        else:
            raise Exception("Unknown visited type: " + ntype)

    # For "untyped" nodes, where visited.getText() is the value, e.g. role names,
    # parameter names, etc.
    def traverse_untyped_leaf(self, node_):
        return self.visit_untyped_leaf(node_)


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
