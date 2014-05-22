import copy

import scrib_util as util

from visit.traverser import Traverser as Traverser

from ast.globel.globalinterruptible import (
    get_scope as globalinterruptible_get_scope,
    EMPTY_SCOPE_NAME as globalinterruptible_EMPTY_SCOPE_NAME,
    get_scope_child as globalinterruptible_get_scope_child,
    get_block_child as globalinterruptible_get_block_child,
    get_interrupt_children as globalinterruptible_get_interrupt_children
)

from ast.globel.globaldo import (
    get_scope as globaldo_get_scope,
    EMPTY_SCOPE_NAME as globaldo_EMPTY_SCOPE_NAME,
    get_scope_child as globaldo_get_scope_child,
    get_argumentlist_child as globaldo_get_argumentlist_child,
    get_roleinstantiationlist_child as globaldo_get_roleinstantiationlist_child,
    get_target_name_children as globaldo_get_target_name_children
)


IMPLICIT_SCOPE_PREFIX = '__'


class ScopeInserter(object):
    def __init__(self):
        super(ScopeInserter, self).__init__()

    # recursive traversal, although some nodes are visited "early" (before going into the
    # children) e.g. sequencing
    def insert_scopes(self, node):
        sc = ScopeCollector()
        scopes = sc.collect_scopes(node)
        sa = ScopeAdder(scopes)
        node = sa.add_scopes(node)
        return node


class ScopeCollector(Traverser):
    def __init__(self):
        super(ScopeCollector, self).__init__()
        self._scopes = {}

    def collect_scopes(self, node_):
        self.traverse(node_)  # Doesn't change node (ignore return)
        return self._scopes

    def visit_untyped_leaf(self, node_):
        return node_


    def _collect_scopes_aux(self, scope):
        self._scopes[scope] = True

    def _visit_module(self, node_):
        return node_

    def _visit_moduledecl(self, node_):
        return node_

    def _visit_importmodule(self, node_):
        return node_

    def _visit_payloadtypedecl(self, node_):
        return node_

    def _visit_globalprotocoldecl(self, node_):
        return node_

    def _visit_roledecllist(self, node_):
        return node_

    def _visit_parameterdecllist(self, node_):
        return node_

    def _visit_globalprotocoldef(self, node_):
        return node_

    def _visit_roleinstantiationlist(self, node_):
        return node_

    def _visit_roleinstantiation(self, node_):
        return node_

    def _visit_argumentlist(self, node_):
        return node_

    def _visit_argument(self, node_):
        return node_

    def _visit_globalprotocolblock(self, node_):
        return node_

    def _visit_globalinteractionsequence(self, node_):
        return node_

    def _visit_globalmessagetransfer(self, node_):
        return node_

    def _visit_messagesignature(self, node_):
        return node_

    def _visit_payload(self, node_):
        return node_

    def _visit_payloadelement(self, node_):
        return node_

    def _visit_globalchoice(self, node_):
        return node_

    def _visit_globalrecursion(self, node_):
        return node_

    def _visit_globalcontinue(self, node_):
        return node_

    def _visit_globalparallel(self, node_):
        return node_

    def _visit_globalinterruptible(self, node_):
        scope = globalinterruptible_get_scope(node_)
        if scope != globalinterruptible_EMPTY_SCOPE_NAME:
            self._collect_scopes_aux(scope)
        return node_

    def _visit_globalinterrupt(self, node_):
        return node_

    def _visit_globaldo(self, node_):
        scope = globaldo_get_scope(node_)
        if scope != globaldo_EMPTY_SCOPE_NAME:
            self._collect_scopes_aux(scope)
        return node_

    def _visit_localprotocoldecl(self, node_):
        return node_

    # Prune local protocols from tree traversal: local protocols cannot have
    # implicit _scopes
    def _traverse_localprotocoldecl(self, node_):
        return node_


class ScopeAdder(Traverser):
    def __init__(self, scopes):
        super(ScopeAdder, self).__init__()
        self._scope = None
        self._scopes = scopes

    def add_scopes(self, node_):
        return self.traverse(node_)

    def visit_untyped_leaf(self, node_):
        return node_


    def _next_scope(self):
        tmp = self._scope
        self._scope = tmp + 1
        return str(tmp)

    def _replace_scope_node(self, scopenode):
        new = copy.deepcopy(scopenode)  # FIXME: avoid deepcopy
        tmp = None
        while True:
            tmp = IMPLICIT_SCOPE_PREFIX + self._next_scope()
            if tmp not in self._scopes:
                self._scopes[tmp] = True  # Not really needed since _next_scope is monotonic
                break
        util.set_node_type(new, tmp)
        return new

    def _visit_module(self, node_):
        self._scope = 1
        return node_

    def _visit_moduledecl(self, node_):
        return node_

    def _visit_importmodule(self, node_):
        return node_

    def _visit_payloadtypedecl(self, node_):
        return node_

    def _visit_globalprotocoldecl(self, node_):
        return node_

    def _visit_roledecllist(self, node_):
        return node_

    def _visit_parameterdecllist(self, node_):
        return node_

    def _visit_globalprotocoldef(self, node_):
        return node_

    def _visit_roleinstantiationlist(self, node_):
        return node_

    def _visit_roleinstantiation(self, node_):
        return node_

    def _visit_argumentlist(self, node_):
        return node_

    def _visit_argument(self, node_):
        return node_

    def _visit_globalprotocolblock(self, node_):
        return node_

    def _visit_globalinteractionsequence(self, node_):
        return node_

    def _visit_globalmessagetransfer(self, node_):
        return node_

    def _visit_messagesignature(self, node_):
        return node_

    def _visit_payload(self, node_):
        return node_

    def _visit_payloadelement(self, node_):
        return node_

    def _visit_globalchoice(self, node_):
        return node_

    def _visit_globalrecursion(self, node_):
        return node_

    def _visit_globalcontinue(self, node_):
        return node_

    def _visit_globalparallel(self, node_):
        return node_

    def _visit_globalinterruptible(self, node_):
        scope = globalinterruptible_get_scope(node_)
        if scope == globalinterruptible_EMPTY_SCOPE_NAME:
            children = []
            scopenode = globalinterruptible_get_scope_child(node_)
            children.append(self._replace_scope_node(scopenode))
            children.append(globalinterruptible_get_block_child(node_))
            children.extend(globalinterruptible_get_interrupt_children(node_))
            node_ = util.antlr_dupnode_and_replace_children(node_, children)
        return node_

    def _visit_globalinterrupt(self, node_):
        return node_

    def _visit_globaldo(self, node_):
        _scope = globaldo_get_scope(node_)
        if _scope == globaldo_EMPTY_SCOPE_NAME:
            children = []
            scopenode = globaldo_get_scope_child(node_)
            children.append(self._replace_scope_node(scopenode))
            children.append(globaldo_get_argumentlist_child(node_))
            children.append(globaldo_get_roleinstantiationlist_child(node_))
            children.extend(globaldo_get_target_name_children(node_))
            node_ = util.antlr_dupnode_and_replace_children(node_, children)
        return node_

    def _visit_localprotocoldecl(self, node_):
        return node_

    def _traverse_localprotocoldecl(self, node_):
        return node_
