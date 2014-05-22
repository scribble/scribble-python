import scrib_constants as constants
import scrib_util as util


#class Visitor:  # old-style class for Python 2.x
class Visitor(object):
    def __init__(self):
        super(Visitor, self).__init__()

    # Visit "typed" AST nodes (type is the getText label); cf. visit_untyped_leaf
    # Should return the visited (possibly updated) node
    def visit(self, node_):
        ntype = util.get_node_type(node_)
        # Because no parameter overloading of methods...
        if ntype == constants.MODULE_NODE_TYPE:
            return self._visit_module(node_)
        elif ntype == constants.MODULE_DECL_NODE_TYPE:
            return self._visit_moduledecl(node_)
        #elif ntype == constants.IMPORT_DECL_NODE_TYPE:
        #    return self._visitImportDecl(node_)
        elif ntype == constants.IMPORT_MODULE_NODE_TYPE:  # FIXME: also members
            return self._visit_importmodule(node_)
        elif ntype == constants.PAYLOAD_DECL_NODE_TYPE:
            return self._visit_payloadtypedecl(node_)
        elif ntype == constants.GLOBAL_PROTOCOL_DECL_NODE_TYPE:
            return self._visit_globalprotocoldecl(node_)
        elif ntype == constants.ROLE_DECL_LIST_NODE_TYPE:
            return self._visit_roledecllist(node_)
        elif ntype == constants.ROLE_DECL_NODE_TYPE:
            return self._visit_roledecl(node_)
        elif ntype == constants.PARAMETER_DECL_LIST_NODE_TYPE:
            return self._visit_parameterdecllist(node_)
        elif ntype == constants.PARAMETER_DECL_NODE_TYPE:
            return self._visit_parameterdecl(node_)
        elif ntype == constants.GLOBAL_PROTOCOL_DEF_NODE_TYPE:
            return self._visit_globalprotocoldef(node_)
        elif ntype == constants.ROLE_INSTANTIATION_LIST_NODE_TYPE:
            return self._visit_roleinstantiationlist(node_)
        elif ntype == constants.ROLE_INSTANTIATION_NODE_TYPE:
            return self._visit_roleinstantiation(node_)
        elif ntype == constants.ARGUMENT_LIST_NODE_TYPE:
            return self._visit_argumentlist(node_)
        elif ntype == constants.ARGUMENT_NODE_TYPE:
            return self._visit_argument(node_)
        elif ntype == constants.GLOBAL_PROTOCOL_BLOCK_NODE_TYPE:
            return self._visit_globalprotocolblock(node_)
        elif ntype == constants.GLOBAL_INTERACTION_SEQUENCE_NODE_TYPE:
            return self._visit_globalinteractionsequence(node_)
        elif ntype == constants.GLOBAL_MESSAGE_TRANSFER_NODE_TYPE:
            return self._visit_globalmessagetransfer(node_)
        elif ntype == constants.MESSAGE_SIGNATURE_NODE_TYPE:
            return self._visit_messagesignature(node_)
        elif ntype == constants.PAYLOAD_NODE_TYPE:
            return self._visit_payload(node_)
        elif ntype == constants.PAYLOAD_ELEMENT_NODE_TYPE:
            return self._visit_payloadelement(node_)
        elif ntype == constants.GLOBAL_CHOICE_NODE_TYPE:
            return self._visit_globalchoice(node_)
        elif ntype == constants.GLOBAL_RECURSION_NODE_TYPE:
            return self._visit_globalrecursion(node_)
        elif ntype == constants.GLOBAL_CONTINUE_NODE_TYPE:
            return self._visit_globalcontinue(node_)
        elif ntype == constants.GLOBAL_PARALLEL_NODE_TYPE:
            return self._visit_globalparallel(node_)
        elif ntype == constants.GLOBAL_INTERRUPTIBLE_NODE_TYPE:
            return self._visit_globalinterruptible(node_)
        elif ntype == constants.GLOBAL_INTERRUPT_NODE_TYPE:
            return self._visit_globalinterrupt(node_)
        elif ntype == constants.GLOBAL_DO_NODE_TYPE:
            return self._visit_globaldo(node_)
        elif ntype == constants.LOCAL_PROTOCOL_DECL_NODE_TYPE:
            return self._visit_localprotocoldecl(node_)
        elif ntype == constants.LOCAL_PROTOCOL_DEF_NODE_TYPE:
            return self._visit_localprotocoldef(node_)
        elif ntype == constants.LOCAL_PROTOCOL_BLOCK_NODE_TYPE:
            return self._visit_localprotocolblock(node_)
        elif ntype == constants.LOCAL_INTERACTION_SEQUENCE_NODE_TYPE:
            return self._visit_localinteractionsequence(node_)
        elif ntype == constants.LOCAL_SEND_NODE_TYPE:
            return self._visit_localsend(node_)
        elif ntype == constants.LOCAL_RECEIVE_NODE_TYPE:
            return self._visit_localreceive(node_)
        elif ntype == constants.LOCAL_CHOICE_NODE_TYPE:
            return self._visit_localchoice(node_)
        elif ntype == constants.LOCAL_RECURSION_NODE_TYPE:
            return self._visit_localrecursion(node_)
        elif ntype == constants.LOCAL_CONTINUE_NODE_TYPE:
            return self._visit_localcontinue(node_)
        elif ntype == constants.LOCAL_PARALLEL_NODE_TYPE:
            return self._visit_localparallel(node_)
        elif ntype == constants.LOCAL_INTERRUPTIBLE_NODE_TYPE:
            return self._visit_localinterruptible(node_)
        elif ntype == constants.LOCAL_THROW_NODE_TYPE:
            return self._visit_localthrow(node_)
        elif ntype == constants.LOCAL_CATCH_NODE_TYPE:
            return self._visit_localcatch(node_)
        elif ntype == constants.LOCAL_DO_NODE_TYPE:
            return self._visit_localdo(node_)
        else:
            raise Exception("Unknown node_ type: " + ntype)
    
    def visit_untyped_leaf(self, node_):
        raise NotImplementedError(util.get_node_type(node_))


    def _visit_module(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_moduledecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    #def _visitImportDecl(self, node_):
    #    raise NotImplementedError(util.get_node_type(node_))

    def _visit_importmodule(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_payloadtypedecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalprotocoldecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_roledecllist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_roledecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_parameterdecllist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_parameterdecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalprotocoldecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalprotocoldef(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_roleinstantiationlist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_roleinstantiation(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_argumentlist(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_argument(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalprotocolblock(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalinteractionsequence(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalmessagetransfer(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_messagesignature(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_payload(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_payloadelement(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalchoice(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalrecursion(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalcontinue(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalparallel(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalinterruptible(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globalinterrupt(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_globaldo(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localprotocoldecl(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localprotocoldef(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localprotocolblock(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localinteractionsequence(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localsend(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localreceive(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localchoice(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localrecursion(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localcontinue(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localparallel(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localinterruptible(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localthrow(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localcatch(self, node_):
        raise NotImplementedError(util.get_node_type(node_))

    def _visit_localdo(self, node_):
        raise NotImplementedError(util.get_node_type(node_))
