from antlr3.tree import CommonErrorNode as CommonErrorNode;

import scrib_util as util

from visit.traverser import Traverser as Traverser


class CommonErrorNodeChecker(Traverser):
    def __init__(self):
        super(CommonErrorNodeChecker, self).__init__()

    # recursive traversal, although some nodes are visited "early" (before going into
    # the children) e.g. sequencing
    def _check_for_errornode(self, node_):
        return self.traverse(node_)

    # Seems certain lexical errors aren't being designated by antlr, e.g. choice
    # role subject "11aa" -- antlr is skipping the bad symbols and producing a
    # normal node (not an error node_)
    def visit_untyped_leaf(self, node_):
        return self._check_for_errornode_aux(node_)

    def _check_for_errornode_aux(self, node_):
        if type(node_) == CommonErrorNode:
        # that's just the way Antlr is working? (error nodes as first child?)
        #if (type(node.getChild(0)) == CommonErrornode_):
            util.report_error(child.toString())
        for child in node_.getChildren():
            if type(child) == CommonErrorNode:
                util.report_error(child.toString())
        return node_


    def _visit_module(self, node_):
        #return module.foo(self, node_)
        return self._check_for_errornode_aux(node_)

    def _visit_moduledecl(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_importmodule(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_payloadtypedecl(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalprotocoldecl(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_roledecllist(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_parameterdecllist(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalprotocoldef(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_roleinstantiationlist(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_roleinstantiation(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_argumentlist(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_argument(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalprotocolblock(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalinteractionsequence(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalmessagetransfer(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_messagesignature(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_payload(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_payloadelement(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalchoice(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalrecursion(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalcontinue(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalparallel(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalinterruptible(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globalinterrupt(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_globaldo(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localprotocoldecl(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localprotocoldef(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localprotocolblock(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localinteractionsequence(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localsend(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localreceive(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localchoice(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localrecursion(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localcontinue(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localparallel(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localinterruptible(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localthrow(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localcatch(self, node_):
        return self._check_for_errornode_aux(node_)

    def _visit_localdo(self, node_):
        return self._check_for_errornode_aux(node_)
