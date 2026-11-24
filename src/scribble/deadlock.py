"""Deadlock checking over a set of local protocol types.

Scribble's deadlock guarantee is discharged a priori.  Section 4.6
well-formedness is checked on the global type
(visit/wellformednesschecker.py), end projection produces each role's local
type (visit/projector.py), and reachability is then checked on each local type
on its own (ast/local/localinteractionsequence.py).  Nothing in that pipeline
ever searches for a *global* blocked state, so a set of local types that is
locally healthy can still deadlock once composed: a circular wait is the
classic case, where each role's own type is fine, every pair of roles can be
merged, and yet no role can move.

This module performs the direct check.  Each local type is compiled to a
labelled transition system whose labels are message transfers; the machines
communicate over one FIFO channel per ordered pair of roles, which is the
asynchronous model of the Scribble theory.  The product of the machines and
the channel contents is explored for a reachable state in which no machine can
move while some machine is unfinished or some channel is non-empty.

The state space is finite for finite local types.  A recursive type makes it
infinite as soon as a message can stay in flight across the recursion body, so
recursion is explored up to a bound on state count and channel occupancy; if
either bound is hit the check reports itself as skipped rather than guess.
The same applies to the local node forms this checker does not model
(interruptible, throw, catch): they are reported as skipped, never as ok.

Entry point: check_module(context, module).  main.py calls it behind the
-deadlock switch, so default scribblec output is unchanged.
"""

import os

import scribble.scrib_constants as constants

from scribble import scrib_util as util

from scribble.ast.roledecl import (
    RoleDecl as RoleDecl,
    has_alias as roledecl_has_alias,
    get_role_name as roledecl_get_role_name,
    get_alias_name as roledecl_get_alias_name,
)
from scribble.ast.messagesignature import (
    pretty_print as messagesignature_pretty_print,
)

from scribble.ast.roledecllist import (
    RoleDeclList as RoleDeclList,
    get_role_names as roledecllist_get_role_names,
    get_roledecl_children as roledecllist_get_roledecl_children,
)

from scribble.ast.module import (
    get_full_name as module_get_full_name,
    get_localprotocoldecl_children as module_get_localprotocoldecl_children,
    get_globalprotocoldecl_children as module_get_globalprotocoldecl_children,
)
from scribble.ast.globel.globalprotocoldecl import (
    get_full_name as globalprotocoldecl_get_full_name,
    get_roledecllist_child as globalprotocoldecl_get_roledecllist_child,
)
from scribble.ast.globel.globaldo import (
    get_projected_member_name as globaldo_get_projected_member_name,
    get_target as globaldo_get_target,
)

from scribble.ast.local.localdo import (
    get_target_name_children as localdo_get_target_name_children,
)
from scribble.ast.local.localprotocoldecl import (
    LocalProtocolDecl as LocalProtocolDecl,
)
from scribble.ast.local.localprotocoldef import (
    LocalProtocolDef as LocalProtocolDef,
)
from scribble.ast.local.localprotocolblock import (
    LocalProtocolBlock as LocalProtocolBlock,
)
from scribble.ast.local.localinteractionsequence import (
    LocalInteractionSequence as LocalInteractionSequence,
)
from scribble.ast.local.localsend import LocalSend as LocalSend
from scribble.ast.local.localreceive import LocalReceive as LocalReceive
from scribble.ast.local.localchoice import LocalChoice as LocalChoice
from scribble.ast.local.localrecursion import LocalRecursion as LocalRecursion
from scribble.ast.local.localcontinue import LocalContinue as LocalContinue
from scribble.ast.local.localdo import LocalDo as LocalDo
from scribble.ast.local.localparallel import LocalParallel as LocalParallel
from scribble.ast.local.localinterruptible import (
    LocalInterruptible as LocalInterruptible,
)
from scribble.ast.local.localthrow import LocalThrow as LocalThrow
from scribble.ast.local.localcatch import LocalCatch as LocalCatch

# Result codes reported by check_system and check_module
OK = 'ok'
DEADLOCK = 'deadlock'
SKIPPED = 'skipped'

# Node kinds in a compiled machine graph
_ACT = 'act'        # op ('send'|'recv'), partners, message, next
_SKIP = 'skip'     # empty choice branch: straight to next
_CHOICE = 'choice'  # branches [entry], next
_PAR = 'par'       # branches [entry], join
_JOIN = 'join'     # end of one par branch, next
_CONT = 'cont'     # jump to cell['target']
_GOTO = 'goto'          # jump to a memoised instantiation
_SET = 'set'       # alts [entry]: branches a peer cannot tell apart
_END = 'end'       # end of the machine

# Local node forms this checker does not model.  Reporting them as skipped is
# the honest answer; guessing would risk either a false report or a false
# all-clear.
_UNSUPPORTED_TYPES = (LocalInterruptible, LocalThrow, LocalCatch)

# Exploration bounds
_MAX_STATES = 200000
_MAX_CHANNEL = 8


class Unsupported(Exception):
    """The local type uses a form this checker does not model."""
    pass


def _message_key(message):
    """The label a transfer contributes to the system.

    Projections carry the message as the string their pretty printer produced
    (see ast/globel/globalmessagetransfer.py:project); parsed local types carry
    the message-signature node.  Both reduce to the same text, payload types
    included, which is the right granularity: two transfers are the same
    label exactly when a role could not tell them apart.
    """
    if message is None:
        return ''
    if isinstance(message, str):
        text = message
    elif message.getChildCount() == 0:
        # A message written without parentheses (`X to B;`) parses to the
        # bare operator token, not to a signature node.
        text = _text(message)
    else:
        text = messagesignature_pretty_print(message)
    return ' '.join(text.split())


def _do_target(tree):
    """The fully qualified target name of a `do`.

    A `do` node keeps its target as a flat run of name tokens after the role
    instantiation list (`(LOCALDO __1 EMPTY_ARGUMENT_LIST (ROLEINSTANTIATIONLIST ...) good misc pack1 P A)`), which is what `get_target_name_children`
returns; joining them with dots gives the member name used for the lookup.
"""
    children = localdo_get_target_name_children(tree)
    return '.'.join(_text(child) for child in children) if children else ''


def _text(node_):
    if node_ is None:
        return ''
    return node_.getText()


# ---------------------------------------------------------------------------
# Raw AST -> class AST
#
# A file is parsed into ANTLR CommonTrees, while the local types in a Context
# are instances of the ast/local classes.  The compiler below is written
# against the class API -- that is the stable interface, and it is what
# projections produce -- so parsed local protocols are converted here.  One
# compiler, one set of accessors.
# ---------------------------------------------------------------------------

def _convert_roledecllist(tree):
    roledecls = []
    for rd in tree.getChildren():
        name = roledecl_get_role_name(rd)
        if roledecl_has_alias(rd):
            roledecls.append(RoleDecl(name, roledecl_get_alias_name(rd)))
        else:
            roledecls.append(RoleDecl(name, None))
    return RoleDeclList(roledecls)


def _convert_item(tree, local_role):
    node_type = util.get_node_type(tree)
    if node_type == constants.LOCAL_SEND_NODE_TYPE:
        dests = [_text(c) for c in tree.getChildren()[1:]]
        return LocalSend(local_role, dests, tree.getChild(0))
    if node_type == constants.LOCAL_RECEIVE_NODE_TYPE:
        return LocalReceive(local_role, _text(tree.getChild(1)),
                             tree.getChild(0))
    if node_type == constants.LOCAL_CHOICE_NODE_TYPE:
        subject = _text(tree.getChild(0))
        blocks = [_convert_block(b, local_role)
                  for b in tree.getChildren()[1:]]
        return LocalChoice(local_role, subject, blocks)
    if node_type == constants.LOCAL_RECURSION_NODE_TYPE:
        label = _text(tree.getChild(0))
        return LocalRecursion(local_role, label,
                              _convert_block(tree.getChild(1), local_role))
    if node_type == constants.LOCAL_CONTINUE_NODE_TYPE:
        return LocalContinue(local_role, _text(tree.getChild(0)))
    if node_type == constants.LOCAL_DO_NODE_TYPE:
        # The target is a dotted member name, which the grammar rewrites as
        # one IDENTIFIER per component: the subtree's own text is just the
        # first component.  Join them the way the rest of the code base does.
        return LocalDo(local_role, _text(tree.getChild(0)),
                       _do_target(tree),
                       tree.getChild(1),
                       _convert_roleinstantiations(tree.getChild(2)))
    if node_type == constants.LOCAL_PARALLEL_NODE_TYPE:
        blocks = [_convert_block(b.getChild(0), local_role)
                  for b in tree.getChildren()]
        return LocalParallel(local_role, blocks)
    raise Unsupported('parsed local interaction of type ' + str(node_type))


def _convert_roleinstantiations(tree):
    roles = []
    for ri in tree.getChildren():
        arg = _text(ri.getChild(0))
        param = _text(ri.getChild(1)) if ri.getChildCount() > 1 else None
        roles.append((arg, param))
    return roles


def _convert_block(tree, local_role):
    node_type = util.get_node_type(tree)
    if node_type == constants.LOCAL_PROTOCOL_BLOCK_NODE_TYPE:
        tree = tree.getChild(0)
    seq = LocalInteractionSequence(local_role,
                                   [_convert_item(item, local_role)
                                    for item in tree.getChildren()])
    return LocalProtocolBlock(local_role, seq)


def _convert_localprotocoldecl(tree):
    local_role = _text(tree.getChild(1))
    body_tree = tree.getChild(4)
    if util.get_node_type(body_tree) != constants.LOCAL_PROTOCOL_DEF_NODE_TYPE:
        raise Unsupported('local protocol body: ' +
                          str(util.get_node_type(body_tree)))
    return LocalProtocolDecl(
        local_role, _text(tree.getChild(0)), tree.getChild(2),
        _convert_roledecllist(tree.getChild(3)),
        LocalProtocolDef([], [], local_role,
                         _convert_block(body_tree.getChild(0), local_role)))


def _as_class_lpd(lpd):
    if isinstance(lpd, LocalProtocolDecl):
        return lpd
    return _convert_localprotocoldecl(lpd)


def _as_class_block(body):
    if isinstance(body, LocalProtocolDef):
        return body.get_block()
    if isinstance(body, LocalProtocolBlock):
        return body
    if isinstance(body, LocalInteractionSequence):
        return LocalProtocolBlock(None, body)
    raise Unsupported('local protocol body of type ' + type(body).__name__)


# ---------------------------------------------------------------------------
# Compilation: one local type -> one machine graph
# ---------------------------------------------------------------------------

def _rolemap(roledecllist_):
    """alias -> name for one local type's role declaration list."""
    mapping = {}
    for rd in roledecllist_.roledecls:
        mapping[rd.alias or rd.name] = rd.name
    return mapping


# A `do` may be self- or mutually recursive.  Its instance is identified by the
# call site together with the role substitution (see _compile_do), so a loop is
# closed as a back edge and needs no unfolding bound at all.  What can still
# grow is the substitution: a cycle that renames roles on every turn is a
# different instance each time, and the bound below turns that into a reported
# skip instead of a hang.
_MAX_INSTANCES = 4      # distinct role substitutions per `do` site
_MAX_EXPORT_STATES = 5000   # graph size above which no DOT file is written

# The export directory is process-wide rather than threaded through every call
# because it is a debugging switch, and a system checked from the module entry
# point is two frames away from the command line that asked for it.
_EXPORT = {'dir': None, 'budget': _MAX_EXPORT_STATES}


def set_export_dir(path):
    """Writes one DOT file per checked system into path; None disables."""
    if path is not None:
        # the writer joins the directory with the file name and opens it, so a
        # missing directory used to lose every graph without an error
        os.makedirs(path, exist_ok=True)
    _EXPORT['dir'] = path


def _instance_key(member_name, role_):
    """The projected instantiation a `do` target belongs to.

    The projection of `do X()` for role C is the member
    '<module>_X_C.X_C', and the projections of the same X for its other roles
    share that prefix.  Keying the renamings on the prefix is what lets the
    machine for A inline X's body with X's own role names replaced by A's
    peers: the projections say, one pairing per role of the instantiation,
    which callee role stands for which caller role.
    """
    if member_name is None or role_ is None:
        return member_name
    module_ = util.get_full_module_name_from_full_member_name(member_name)
    simple = util.get_simple_member_name_from_full_member_name(member_name)
    suffix = '_' + role_
    if not simple.endswith(suffix):
        return member_name
    proto = simple[:-len(suffix)]
    prefix = '_' + proto + '_' + role_
    if not module_.endswith(prefix):
        return member_name
    return module_[:-len(prefix)] + '.' + proto


def _renames_of(lpds, resolve):
    """callee role -> caller role, per instantiated protocol.

    A `do` in a projection carries no role instantiations: the projector has
    already specialised the call, so the call names only the member projected
    for *this* role, and the callee's body still names its own roles.  The
    correspondence is therefore read off the projections themselves -- role C
    instantiates as role A exactly when A's projection calls C's projection --
    which is the same positional rewrite the global type describes.

    A callee role reached from two different caller roles for one target has
    no single reading here; that instantiation is marked and refused rather
    than guessed.
    """
    table = {}
    for lpd in lpds:
        caller = lpd.get_local_role()
        if caller is None:
            continue
        for target in _do_targets(lpd):
            try:
                callee = resolve(target)
            except Unsupported:
                continue
            if callee is None:
                continue
            callee_role = callee.get_local_role()
            if callee_role is None or callee_role == caller:
                continue
            key = _instance_key(target, callee_role)
            entry = table.get(key, {})
            if entry is False:
                continue
            known = entry.get(callee_role)
            if known is not None and known != caller:
                table[key] = False
                continue
            entry[callee_role] = caller
            table[key] = entry
    return table


_SITES = {}
_SITE_COUNT = [0]


def _site_of(item):
    """A stable identity for one syntactic `do`, surviving re-instantiation.

    A protocol that instantiates itself is compiled from the same AST nodes on
    every turn of the cycle, so node identity is the call site.  The node is
    held in the table to keep its id from being reused by a later object, and
    the identity check guards the entry itself.
    """
    entry = _SITES.get(id(item))
    if entry is None or entry[0] is not item:
        _SITE_COUNT[0] += 1
        entry = (item, _SITE_COUNT[0])
        _SITES[id(item)] = entry
    return entry[1]


class _Compiler(object):
    def __init__(self, role, resolve, renames=None):
        self.role = role
        self.resolve = resolve          # do target -> class LocalProtocolDecl
        self.renames = renames or {}    # instantiation key -> {callee: caller}
        self.graph = []
        self.instances = {}             # (site, substitution) -> (entry, continuation)

    def _new(self, node):
        node['id'] = len(self.graph)
        self.graph.append(node)
        return node['id']

    def _indirect(self):
        """A node that only says "carry on at the cell's target"."""
        cell = {'target': -1}
        return self._new({'kind': _GOTO, 'cell': cell}), cell

    def compile(self, lpd):
        end = self._new({'kind': _END})
        entry = self._compile_body(lpd, lpd.get_body(), end, {}, {})
        return {'role': self.role, 'graph': self.graph, 'start': entry,
                'end': end}

    # -- bodies ----------------------------------------------------------

    def _compile_body(self, lpd, body, next_, renames, labels):
        # A local type's own messages name its peers by the aliases in its role
        # declaration list (`role Client as C`), while a machine is identified
        # by the role name.  Start the renaming with that declaration's own
        # aliases and layer the caller's instantiation on top.
        inner = _rolemap(lpd.get_roledecllist())
        inner.update(renames)
        return self._compile_block(_as_class_block(body), next_, inner, labels)

    def _compile_block(self, block, next_, renames, labels):
        return self._compile_sequence(block.get_localinteraction_sequence(),
                                      next_, renames, labels)

    def _compile_sequence(self, seq, next_, renames, labels):
        entry = next_
        for item in reversed(seq.get_children()):
            entry = self._compile_item(item, entry, renames, labels)
        return entry

    def _role(self, name, renames):
        return renames.get(name, name)

    def _compile_item(self, item, next_, renames, labels):
        if isinstance(item, LocalSend):
            dests = tuple(self._role(d, renames)
                          for d in item.get_destinations())
            return self._new({'kind': _ACT, 'op': 'send', 'partners': dests,
                              'message': _message_key(item.get_message()),
                              'next': next_})
        if isinstance(item, LocalReceive):
            return self._new({'kind': _ACT, 'op': 'recv',
                              'partners': (self._role(item.get_source(),
                                                      renames),),
                              'message': _message_key(item.get_message()),
                              'next': next_})
        if isinstance(item, LocalChoice):
            branches = [self._compile_block(_as_class_block(block), next_,
                                            renames, labels)
                        for block in item.get_block_children()]
            return self._new({'kind': _CHOICE, 'branches': branches,
                              'next': next_})
        if isinstance(item, LocalParallel):
            join = self._new({'kind': _JOIN, 'next': next_})
            branches = [self._compile_block(_as_class_block(block), join,
                                            renames, labels)
                        for block in item.get_block_children()]
            return self._new({'kind': _PAR, 'branches': branches,
                              'join': join})
        if isinstance(item, LocalRecursion):
            cell = {'target': -1}
            inner = dict(labels)
            inner[item.get_label()] = cell
            entry = self._compile_block(_as_class_block(item.get_block_child()),
                                        next_, renames, inner)
            cell['target'] = entry
            return entry
        if isinstance(item, LocalContinue):
            if item.get_label() not in labels:
                raise Unsupported('continue without a matching recursion: ' +
                                  str(item.get_label()))
            return self._new({'kind': _CONT,
                              'cell': labels[item.get_label()]})
        if isinstance(item, LocalDo):
            return self._compile_do(item, next_, renames, labels)
        if isinstance(item, _UNSUPPORTED_TYPES):
            raise Unsupported(type(item).__name__)
        raise Unsupported('local interaction of type ' + type(item).__name__)

    def _compile_do(self, item, next_, renames, labels):
        target = item.get_target()
        target_ = self.resolve(target)
        if target_ is None:
            raise Unsupported('instantiation of unknown local protocol ' +
                              str(target))
        sub = self._do_substitution(target_, item, renames)
        # Instantiation is inlined, but a protocol that instantiates itself,
        # directly or through another one, has to become a cycle in the graph
        # or the state space is unbounded.  The identity of an instance is the
        # call site together with the role substitution, so a second entry
        # through the same site with the same substitution is the same state:
        # the edge closes and the recursion is a fixpoint, not a sequence of
        # unfoldings.  That makes the state space finite without any depth
        # bound, which is what the coinductive treatment of recursion in the
        # other Scribble checkers amounts to.
        #
        # The one thing that identity does not capture is the continuation.
        # A `do` in tail position returns to the continuation it was called
        # with, so the closed edge is exact; a `do` in the scope of a recursion
        # body can be re-entered with a fresher continuation, and reusing the
        # first one would silently swap the two.  That case is refused rather
        # than approximated, because an approximation here would move behaviour
        # between machines and no verdict would mean anything afterwards.
        key = (_site_of(item), tuple(sorted(sub.items())))
        known = self.instances.get(key)
        if known is not None:
            if known[1] != next_:
                raise Unsupported(
                    'recursive instantiation of ' + str(target) + ' whose ' +
                    'continuation is not in tail position')
            return known[0]
        same_site = [k for k in self.instances if k[0] == key[0]]
        if len(same_site) >= _MAX_INSTANCES:
            raise Unsupported('recursive instantiation of ' + str(target) +
                              ' with unboundedly many role renamings')
        entry, cell = self._indirect()
        self.instances[key] = (entry, next_)
        body = self._compile_body(target_, target_.get_body(), next_, sub,
                                  labels)
        cell['target'] = body
        return entry

    def _do_substitution(self, target_, item, renames):
        """The renaming that inlines a callee into the caller's role scope.

        Role instantiation reads '<caller role> as <callee role>': inside a
        local type whose own roles are Consumer and Producer the projector
        writes

            do __1: popl14.X.NegotiateAux_CounterParty.NegotiateAux_CounterParty
                    (Consumer as Proposer, Producer as CounterParty)

        against a callee declared 'role Proposer as A, role CounterParty as B'.
        The left names are in the caller's scope, where they may be aliases of
        the caller's own declaration; the right names are the callee's role
        names, and the callee body may use either those names or its own
        aliases, so both spellings are mapped onto the caller.
        """
        callee = _rolemap(target_.get_roledecllist())
        sub = dict(renames)
        # The projected `do` keeps a role parameter only where the source wrote
        # one (`do X(A as D)`); the plain form `do X(A, B)` leaves them empty
        # even though the positional correspondence with X's role declaration
        # list is exactly the substitution.  Reading it off the projections
        # alone recovers only the role this type projects to, so a callee that
        # names any other role (Pack13's D, reached from A's projection of
        # Pack13_C) arrived unrenamed and the closure check refused the
        # system.  Worse, the projections of a protocol instantiated from two
        # different callers record two caller-side spellings under one member
        # name, so that table has no single reading at all.
        #
        # Position is authoritative because it is what the source says: one
        # role instantiation per role of the callee, in declaration order.
        # The projection-derived table is consulted only for the shapes where
        # the two lists do not line up.
        decls = [rd.name for rd in target_.get_roledecllist().roledecls]
        ris = item.get_roleinstantiations()
        if len(decls) == len(ris):
            for (formal, (caller_name, _param)) in zip(decls, ris):
                sub[callee.get(formal, formal)] = self._role(caller_name,
                                                             renames)
        else:
            extra = self.renames.get(
                _instance_key(item.get_target(), target_.get_local_role()), {})
            if extra is False:
                raise Unsupported('conflicting instantiations of ' +
                                  str(item.get_target()))
            for (callee_name, caller_name) in extra.items():
                sub[callee_name] = self._role(caller_name, renames)
        for (caller_name, callee_name) in item.get_roleinstantiations():
            if callee_name is None:
                continue
            callee_name = callee.get(callee_name, callee_name)
            sub[callee_name] = self._role(caller_name, renames)
        for alias, name in callee.items():
            if name in sub:
                sub[alias] = sub[name]
        return sub



# ---------------------------------------------------------------------------
# Running the system: machines plus FIFO channels
# ---------------------------------------------------------------------------

def _resolve(graph, idx):
    seen = set()
    while graph[idx]['kind'] in (_CONT, _GOTO):
        if idx in seen:
            raise Unsupported('recursion body with no interaction')
        seen.add(idx)
        idx = graph[idx]['cell']['target']
    return idx


def _normalise(graph, threads):
    """Resolves jumps, expands par nodes, collapses finished par blocks.

    A thread tuple belongs to one role: one entry per live parallel branch,
    a single entry otherwise.  Keeping it per role matters, because otherwise
    two roles finishing a parallel block at the same time collapse into one.
    """
    threads = tuple(threads)
    while True:
        out = []
        for idx in threads:
            idx = _resolve(graph, idx)
            node = graph[idx]
            if node['kind'] == _PAR:
                out.extend(node['branches'])
            else:
                out.append(idx)
        threads = tuple(out)
        if len(threads) > 1 and len(set(threads)) == 1:
            node = graph[threads[0]]
            if node['kind'] == _JOIN:
                threads = (node['next'],)
                continue
        return threads


def _frontier(graph, threads):
    """Yields (op, successor thread tuple) for the actions available now."""
    out = []
    for i, idx in enumerate(tuple(threads)):
        for (op, succ) in _frontier_one(graph, idx):
            advanced = list(threads)
            advanced[i:i + 1] = list(succ)
            out.append((op, _normalise(graph, advanced)))
    return out


def _head_op(graph, idx):
    """The single action a branch starts with, or None if it starts with more.

    A branch starting with a nested `par` or a nested `choice` has no single
    head, and one starting at a `join` has none at all.
    """
    if not _resolves(graph, idx):
        return None
    ops = _frontier_one(graph, idx)
    if len(ops) != 1:
        return None
    return ops[0][0]


def _resolves(graph, idx):
    try:
        _resolve(graph, idx)
    except Unsupported:
        return False
    return True


def _choice_moves(graph, node):
    """The moves a local choice offers its own role.

    Which one this is depends on the branches, not on how the choice was
    written.  When every branch starts by receiving from the same peer the
    choice is *external*: the peer decides, and the role learns which branch
    it is in by the message it receives, so a branch is entered by that
    receive and nothing else.  Otherwise the role itself decides, and it does
    so *now*: it commits to a branch even when the branch's first action
    cannot happen yet.  Letting a committed choice wait for its first action
    to be enabled instead would quietly drop every deadlock in which a role
    guesses wrong about what its peer is going to send, which is the classic
    asymmetric-choice failure (`bad/safety/waitfor` in scribble-java).
    """
    branches = [b for b in node['branches']]
    out = []
    external = not _role_decides(graph, node)
    if external:
        return _external_moves(graph, node, branches)
    for branch in branches:
        if branch == node['next']:
            out.append((('skip', (), ''), (node['next'],)))
        else:
            out.append((('skip', (), ''), (branch,)))
    return out


def _external_moves(graph, node, branches):
    """The moves of a role that learns its branch from the message it gets.

    Each branch is entered by its first action and nothing else, which is right
    while the branches differ there: the message says which one the peer took.
    When two branches begin with the same transfer they are one move with two
    continuations, and the peer has not committed to either from this role's
    point of view -- the decider's commitment is internal to the decider and
    nothing about it reaches the wire.  Taking them as separate moves lets the
    two roles disagree about the branch (one in branch one, the other in branch
    two), which is a state the protocol cannot reach and which the search then
    reports as a deadlock; that is what `good/todo/Do04c` in scribble-java
    looks like once its instantiations are inlined.  So a shared head becomes a
    single move into the set of branch entries, and a role standing in such a
    set may take any branch's moves or count as finished if one of them ends.
    """
    heads = {}
    for branch in branches:
        for (op, succ) in _frontier_one(graph, branch):
            heads.setdefault(op, []).append((branch, succ))
    out = []
    for op in heads:
        entries = heads[op]
        if len(entries) == 1:
            out.append((op, entries[0][1]))
            continue
        alts = [succ[0] for (branch, succ) in entries
                if len(succ) == 1 and succ[0] != -1]
        if len(alts) != len(entries):
            # a branch that expands to several parallel threads has no single
            # entry to put in the set; keep the branches apart, as before.
            for (branch, succ) in entries:
                out.append((op, succ))
            continue
        out.append((op, (_set_node(graph, node, alts),)))
    return out


def _set_node(graph, node, alts):
    """One graph node standing for a set of branch entries, made once per set."""
    alts = tuple(alts)
    cache = node.setdefault('_sets', {})
    if alts not in cache:
        cache[alts] = None
        cache[alts] = len(graph)
        graph.append({'id': len(graph), 'kind': _SET, 'alts': alts})
    return cache[alts]


def _role_decides(graph, node, seen=None):
    """Whether the role at this choice has to pick a branch itself.

    A branch whose head is another choice has no first action of its own, so
    the test has to look through it.  Otherwise a nested external choice --
    `choice at B { l1() from B to A; choice at A {...} } or { choice at B {...} }`
    -- looks like a branch with no receive in it, the role is taken to commit
    before the peer has sent anything, and a perfectly live protocol is
    reported as a deadlock.  That is the shape of
    good/misc/globals/gchoice/Choice05a in scribble-java.
    """
    seen = seen if seen is not None else set()
    for branch in node['branches']:
        idx = _resolve(graph, branch)
        if idx in seen:
            continue
        seen.add(idx)
        inner = graph[idx]
        kind = inner['kind']
        if kind == _ACT and inner['op'] == 'recv':
            continue
        if kind == _CHOICE:
            if _role_decides(graph, inner, seen):
                return True
            continue
        # send, skip, par, join: the role can move without hearing from a peer
        return True
    return False


def _frontier_one(graph, idx):
    """Yields (op, successor thread tuple) for the actions available at idx."""
    idx = _resolve(graph, idx)
    node = graph[idx]
    kind = node['kind']
    if kind == _ACT:
        return [((node['op'], node['partners'], node['message']),
                 (node['next'],))]
    if kind == _SKIP:
        return [(('skip', (), ''), (node['next'],))]
    if kind == _CHOICE:
        return _choice_moves(graph, node)
    if kind == _SET:
        out = []
        for alt in node['alts']:
            out.extend(_frontier_one(graph, alt))
        return out
    if kind == _PAR:
        base = node['branches']
        out = []
        for i in range(len(base)):
            for (op, succ) in _frontier_one(graph, base[i]):
                advanced = list(base)
                advanced[i:i + 1] = list(succ)
                out.append((op, _normalise(graph, advanced)))
        return out
    return []


class _System(object):
    def __init__(self, machines):
        self.machines = machines
        self.roles = sorted(machines.keys())

    def start_state(self):
        return (tuple((self.machines[role]['start'],) for role in self.roles), {})

    def key(self, state):
        positions, channels = state
        encoded = tuple((sender, receiver,
                         tuple(channels[(sender, receiver)]))
                        for (sender, receiver) in sorted(channels.keys()))
        return (positions, encoded)

    def _moves_of_role(self, i, positions, channels):
        """Actions role i can take now, as (action, next-state) pairs."""
        role = self.roles[i]
        graph = self.machines[role]['graph']
        out = []
        for (op, succ) in _frontier(graph, positions[i]):
            kind = op[0]
            if kind == 'skip':
                new_positions = list(positions)
                new_positions[i] = _normalise(graph, succ)
                out.append((('skip', role, '', ''),
                            (tuple(new_positions), channels)))
            elif kind == 'send':
                partners, msg = op[1], op[2]
                for dest in partners:
                    if dest not in self.machines:
                        continue
                    if len(channels.get((role, dest), [])) >= _MAX_CHANNEL:
                        continue
                    new_channels = dict((k, list(v))
                                        for (k, v) in channels.items())
                    new_channels.setdefault((role, dest), []).append(msg)
                    new_positions = list(positions)
                    new_positions[i] = _normalise(graph, succ)
                    out.append((('send', role, dest, msg),
                                (tuple(new_positions), new_channels)))
            else:
                if not op[1]:
                    continue
                src, msg = op[1][0], op[2]
                queue = channels.get((src, role), [])
                if not queue or queue[0] != msg:
                    continue
                new_channels = dict((k, list(v))
                                    for (k, v) in channels.items())
                new_channels[(src, role)] = queue[1:]
                new_positions = list(positions)
                new_positions[i] = _normalise(graph, succ)
                out.append((('recv', role, src, msg),
                            (tuple(new_positions), new_channels)))
        return out

    def transitions(self, state):
        positions, channels = state
        out = []
        for i, role in enumerate(self.roles):
            for (action, next_state) in self._moves_of_role(i, positions,
                                                            channels):
                out.append((action, action[3], next_state))
        return out

    def finished(self, state):
        positions, channels = state
        for key_ in channels:
            if channels[key_]:
                return False
        for i, role in enumerate(self.roles):
            # A role is finished when its head resolves to the end of its
            # machine, not when the head index happens to equal the index the
            # end node was created at: parallel branches and the joins that
            # close them reach that node through cells and jumps, and an index
            # comparison calls such a role unfinished while `blocked_roles`
            # calls it finished, which is how a module whose every role is done
            # used to be reported as a deadlock.
            thread = positions[i]
            if len(thread) != 1:
                return False
            graph = self.machines[role]['graph']
            if not _at_end(graph, thread[0]):
                return False
        return True

    def bound_hit(self, i, positions, channels):
        """A send the channel bound kept role i from taking, or None.

        The bound exists to keep the state space finite, but a state blocked
        only because a channel is full is not a deadlock: on a longer channel
        the send would happen.  `explore` refuses such a state rather than
        reporting it, because a verdict here would be a false positive.
        """
        role = self.roles[i]
        graph = self.machines[role]['graph']
        for (op, _succ) in _frontier(graph, positions[i]):
            if op[0] != 'send':
                continue
            for dest in op[1]:
                if dest in self.machines and \
                        len(channels.get((role, dest), [])) >= _MAX_CHANNEL:
                    return (role, dest, op[2])
        return None

    def blocked_roles(self, state):
        """Roles with no enabled action, each with a one-line reason."""
        positions, channels = state
        report = []
        for i, role in enumerate(self.roles):
            if self._moves_of_role(i, positions, channels):
                continue
            graph = self.machines[role]['graph']
            idx = _resolve(graph, positions[i][0])
            node = graph[idx]
            if node['kind'] == _SET and _at_end(graph, positions[i][0]):
                report.append((role, 'finished'))
            elif node['kind'] == _END:
                report.append((role, 'finished'))
            elif node['kind'] == _JOIN:
                report.append((role, 'finished inside a parallel block'))
            else:
                report.append((role, _describe(node, channels, role,
                                               set(self.machines))))
        return report


def _at_end(graph, idx):
    """Whether a thread head has run out of actions.

    A set head is finished when any of its branches ends: the role could be in
    that branch, so a search that stopped here has not found a role with work
    it cannot do.
    """
    idx = _resolve(graph, idx)
    node = graph[idx]
    if node['kind'] == _SET:
        return any(_at_end(graph, alt) for alt in node['alts'])
    return node['kind'] == _END


def _describe(node, channels, role, present=None):
    if node['kind'] == _ACT:
        if node['op'] == 'send':
            absent = [p for p in node['partners']
                      if present is not None and p not in present]
            if absent:
                return 'wanted to send ' + node['message'] + ' to ' + \
                       ', '.join(absent) + ', but no such role is ' \
                       'in the system'
            return 'wanted to send ' + node['message'] + ' to ' + \
                   ', '.join(node['partners']) + ', but the channel is ' \
                   'full (' + str(_MAX_CHANNEL) + ' messages, which is ' \
                   'the model bound)'
        joiner = ' from '
        src = node['partners'][0] if node['partners'] else '?'
        queue = channels.get((src, role), [])
        if not queue:
            return 'waiting for ' + node['message'] + joiner + src + \
                   ', which has not been sent'
        return 'waiting for ' + node['message'] + joiner + src + \
               ', but ' + repr(queue[0]) + ' is at the head of that channel'
    if node['kind'] == _CHOICE:
        return 'a choice none of whose branches can start'
    if node['kind'] == _SET:
        return ('a choice of ' + str(len(node['alts'])) + ' branches, none of '
                'which can start')
    return node['kind']


def explore(system, name=None):
    """Breadth-first search of the reachable states for a dead one.

    The queue is a list walked by index and every state is expanded once, so
    the first dead state found is one with a shortest run reaching it: the
    trace is the shortest counterexample, not any counterexample.  A deadlock
    is a state with no enabled action that is not a state in which every role
    has finished, which is the asynchronous-session definition (a role alone on
    a channel, or a channel with traffic no one will take, is a deadlock even
    when no single role is "waiting for a message that was never sent").
    """
    start = system.start_state()
    start_key = system.key(start)
    parents = {start_key: None}
    trace_action = {}
    edges = []
    queue = [start]
    transitions = 0
    index = 0
    dead = None
    result = None
    while index < len(queue):
        state = queue[index]
        index += 1
        moves = system.transitions(state)
        transitions += len(moves)
        key = system.key(state)
        if not moves:
            if system.finished(state):
                continue
            positions_, channels_ = state
            hit = None
            for i in range(len(system.roles)):
                if system._moves_of_role(i, positions_, channels_):
                    continue
                hit = system.bound_hit(i, positions_, channels_)
                if hit is not None:
                    break
            if hit is not None:
                # Blocked only because a channel reached its bound: not a
                # deadlock, so refuse instead of reporting, exactly as an
                # exhausted budget is refused.
                result = {'status': SKIPPED, 'states': len(parents),
                          'transitions': transitions, 'depth': -1,
                          'reason': 'channel bound ' + str(_MAX_CHANNEL) +
                                    ' reached on ' + hit[0] + ' -> ' + hit[1]}
                break
            dead = key
            trace = []
            while key is not None:
                action = trace_action.get(key)
                if action is not None:
                    trace.append(action)
                key = parents[key]
            trace.reverse()
            result = {'status': DEADLOCK, 'states': len(parents),
                      'transitions': transitions, 'depth': len(trace),
                      'kind': _deadlock_kind(system.blocked_roles(state)),
                      'blocked': system.blocked_roles(state), 'trace': trace}
            break
        for (action, _msg, next_state) in moves:
            next_key = system.key(next_state)
            edges.append((system.key(state), next_key, action))
            if next_key in parents:
                continue
            if len(parents) >= _MAX_STATES:
                result = {'status': SKIPPED, 'states': len(parents),
                          'transitions': transitions, 'depth': -1,
                          'reason': 'state bound ' + str(_MAX_STATES) +
                                    ' reached'}
                break
            parents[next_key] = system.key(state)
            trace_action[next_key] = action
            queue.append(next_state)
        if result is not None:
            break
    if result is None:
        result = {'status': OK, 'states': len(parents),
                  'transitions': transitions, 'depth': -1}
    if name is not None:
        _export_dot(system, name, parents, edges, dead)
    return result


def _check_role_closure(machines):
    """Refuses a projection that talks to a role its protocol does not have."""
    for role in sorted(machines):
        for node in machines[role]['graph']:
            if node.get('kind') != _ACT:
                continue
            for partner in node['partners']:
                if partner in machines:
                    continue
                raise Unsupported(
                    'the projection for ' + str(role) + ' talks to ' +
                    str(partner) + ', which is not a role of the protocol')


def _deadlock_kind(blocked):
    """Classifies a dead state from the reasons its roles are stuck.

    The three shapes are worth telling apart because they have different
    causes: `stuck` is a channel whose head nobody wants (the parties disagree
    about the order of messages on one channel), `unfinished` is a role that
    has run out of protocol while a peer still expects to talk to it, and
    `wait-for` is a circular wait, which is the shape Section 4.6 excludes by
    construction and the one a hand-written set of local types usually breaks.
    """
    reasons = [reason for (_role, reason) in blocked]
    if any('is at the head of that channel' in reason for reason in reasons):
        return 'stuck'
    if any(reason.startswith('finished') for reason in reasons):
        return 'unfinished'
    return 'wait-for'


def _dot_id(name):
    return ''.join(c if (c.isalnum() or c in '-_.') else '_' for c in name)


def _export_dot(system, name, parents, edges, dead):
    """Writes the explored graph of this system as one DOT file, opt-in.

    Off unless a directory was given on the command line, and skipped when the
    graph exceeds its budget: the point of the file is to look at a
    counterexample, and a file nobody can open is worse than no file.
    """
    if _EXPORT['dir'] is None:
        return
    if len(parents) > _EXPORT['budget']:
        return
    ids = {}
    for key in parents:
        ids[key] = 's' + str(len(ids))
    lines = ['digraph "' + _dot_id(name) + '" {', '  rankdir=LR;',
             '  node [shape=circle, fontname="Helvetica", fontsize=9];']
    for key, ident in ids.items():
        attrs = []
        if parents[key] is None:
            attrs.append('shape=doublecircle')
        if key is dead:
            attrs.append('color=red')
            attrs.append('penwidth=2')
        lines.append('  ' + ident + ' [label="' + ident + '"' +
                     (', ' + ', '.join(attrs) if attrs else '') + '];')
    for (from_key, to_key, action) in edges:
        if from_key not in ids or to_key not in ids:
            continue
        # A send is drawn dashed against the receive that consumes it, so the
        # two halves of one transfer are visually paired in the file.
        style = '' if action[0] == 'recv' else ', style=dashed'
        lines.append('  ' + ids[from_key] + ' -> ' + ids[to_key] +
                     ' [label="' + _format_action(action).replace('"', "'") +
                     '"' + style + '];')
    lines.append('}')
    path = os.path.join(_EXPORT['dir'], _dot_id(name) + '.dot')
    handle = open(path, 'w')
    try:
        handle.write('\n'.join(lines) + '\n')
    finally:
        handle.close()


def _format_action(action):
    kind, role, partner, msg = action
    if kind == 'send':
        return role + ': send ' + msg + ' to ' + partner
    if kind == 'recv':
        return role + ': receive ' + msg + ' from ' + partner
    return role + ': resolve a choice'


def _member_candidates(context_, target):
    """The member names a `do` target may be listed under.

    The target is either already fully qualified, or it starts with a module
    alias from an `import ... as X` (`do Pack16.Pack16(A, B)`), in which case
    the alias is replaced by the module name it stands for.
    """
    yield target
    head, _, rest = target.partition('.')
    if not rest:
        return
    try:
        modules = context_.get_visible_modules()
    except Exception:
        return
    for alias in list(modules):
        if alias != head:
            continue
        module = modules[alias]
        base = module.get_name() if hasattr(module, 'get_name') else alias
        if base and base != alias:
            yield base + '.' + rest


def _resolver(context_, lpds, pool=()):
    """Resolves a `do` target against this system, then the module context.

    A projection instantiates its target by fully qualified member name
    (popl14.Negotiation2_NegotiateAux_CounterParty.NegotiateAux_CounterParty),
    while a hand-written module uses the bare protocol name.  Both are looked
    up; the context case is what pulls a separately declared local protocol,
    such as one projecting a `do` in another global protocol, into the type
    being compiled.
    """
    by_name = {}
    for lpd in tuple(lpds) + tuple(pool):
        by_name[lpd.get_name()] = lpd
        by_name[lpd.get_name().split('.')[-1]] = lpd

    def resolve(target):
        target_ = by_name.get(target) or by_name.get(target.split('.')[-1])
        if target_ is not None:
            return target_
        if context_ is not None and context_.has_projection(target):
            member = context_.get_projection(target)
            return by_name.setdefault(target,
                                      _as_class_lpd(member))
        if context_ is not None:
            # A local protocol declared in another module, instantiated by its
            # fully qualified member name (`do m.p.Prot(A)`).  `get_member`
            # indexes its table directly and raises KeyError for a miss.
            for name in _member_candidates(context_, target):
                try:
                    member = context_.get_member(name)
                except KeyError:
                    continue
                if member is not None and \
                        util.get_node_type(member) == \
                        constants.LOCAL_PROTOCOL_DECL_NODE_TYPE:
                    return by_name.setdefault(name,
                                              _as_class_lpd(member))
        return None

    return resolve


def _check_roles_present(machines):
    """Refuse a system that addresses a role it does not contain.

    A local protocol may name a role for which the module (or projection set)
    carries no local type.  Such a system is partial: the addressed role never
    runs, so every send to it blocks and the search would report a deadlock
    that the file does not have.  Incomplete input is refused, not reported.
    """
    present = set(machines)
    for role, machine in machines.items():
        for node in machine['graph']:
            for partner in node.get('partners', ()):
                if partner not in present:
                    raise Unsupported('role ' + str(partner) + ' is addressed '
                                      'by ' + str(role) + ' but has no local '
                                      'type in this module')


def check_system(lpds, name=None, context_=None, pool=(), projected=False):
    """Checks one system, given the local types that compose it.

    `projected` says the local types are the projection of one global type.  A
    projection cannot address a role outside its protocol, so a machine that
    does means the projection is not of that global type and the model is not
    the composition the global type prescribes; that is refused rather than
    reported, because the deadlock it would find is a deadlock in our own
    reading of the file, not in the file.
    """
    name = name or '<system>'
    lines = []
    try:
        lpds = [_as_class_lpd(lpd) for lpd in lpds]
        pool_ = []
        for lpd in pool:
            try:
                pool_.append(_as_class_lpd(lpd))
            except Unsupported:
                continue
        resolve = _resolver(context_, lpds, pool_)
        renames = _renames_of(lpds + pool_, resolve)
        machines = {}
        for lpd in lpds:
            role = lpd.get_local_role()
            if role in machines:
                raise Unsupported('two local types for role ' + str(role))
            machines[role] = _Compiler(role, resolve, renames).compile(lpd)
        if projected:
            _check_role_closure(machines)
        _check_roles_present(machines)
        report = explore(_System(machines), name=name)
    except Unsupported as exc:
        lines.append('[Deadlock] ' + name + ': not checked: ' + str(exc))
        return {'status': SKIPPED, 'name': name, 'report': lines}
    if report['status'] == DEADLOCK:
        lines.append('[Deadlock] ' + name + ': deadlock (' +
                     report['kind'] + ')')
        for (role, reason) in report['blocked']:
            lines.append('[Deadlock]   ' + str(role) + ': ' + reason)
        if report['trace']:
            steps = report['depth']
            lines.append('[Deadlock]   shortest trace (' + str(steps) +
                         (' step' if steps == 1 else ' steps') + ') over ' +
                         str(report['states']) + ' states:')
            for action in report['trace']:
                lines.append('[Deadlock]     ' + _format_action(action))
    elif report['status'] == OK:
        lines.append('[Deadlock] ' + name + ': ok (' + str(report['states']) +
                     ' states, ' + str(report['transitions']) +
                     ' transitions)')
    elif report['status'] == SKIPPED:
        lines.append('[Deadlock] ' + name + ': not checked: ' +
                     report['reason'])
    report['name'] = name
    report['report'] = lines
    return report


# ---------------------------------------------------------------------------
# Module entry point
# ---------------------------------------------------------------------------

def _do_targets(lpd):
    """Names of local protocols instantiated by do anywhere in this type."""
    targets = []

    def walk_block(block):
        for item in _as_class_block(block).get_localinteraction_sequence().get_children():
            if isinstance(item, LocalDo):
                targets.append(item.get_target())
            elif isinstance(item, LocalChoice):
                for b in item.get_block_children():
                    walk_block(b)
            elif isinstance(item, LocalRecursion):
                walk_block(item.get_block_child())
            elif isinstance(item, LocalParallel):
                for b in item.get_block_children():
                    walk_block(b)

    try:
        walk_block(lpd.get_body())
    except Unsupported:
        pass
    return targets


def _root_localprotocoldecls(module_):
    lpds = [_as_class_lpd(lpd)
            for lpd in module_get_localprotocoldecl_children(module_)]
    used = set()
    for lpd in lpds:
        for name in _do_targets(lpd):
            used.add(name)
            used.add(name.split('.')[-1])
    roots = [lpd for lpd in lpds
             if lpd.get_name() not in used and
             lpd.get_name().split('.')[-1] not in used]
    # Mutual instantiation leaves no root: the protocols form one cycle and
    # compose with each other, so the whole module is the system.
    return roots or lpds


def _systems_of_module(context_, module_):
    """Groups a module's local types into systems.

    A global protocol's projections are one system, the composition that global
    type prescribes, and `check_projections` has already checked those.  What is
    left is the module's own local protocols, which are a system of their own
    only when they are not merely the projections of a global type just
    checked; a module of locals and no globals is the choreography itself.
    """
    roots = _root_localprotocoldecls(module_)
    if not roots:
        return []
    return [(module_get_full_name(module_), roots)]


def _systems_from_projections(context_, module_):
    """Systems induced by the projections of each global protocol.

    A module that declares only global types has no local protocol
    declarations to check, but main.py has already produced every projection,
    so the same search runs over exactly the local types Scribble would emit.
    That is the input a global-first checker such as scribble-java works on.
    """
    systems = []
    for gpd in module_get_globalprotocoldecl_children(module_):
        full_name = globalprotocoldecl_get_full_name(gpd)
        rdl = globalprotocoldecl_get_roledecllist_child(gpd)
        lpds = []
        for rd in roledecllist_get_roledecl_children(rdl):
            role_ = roledecl_get_role_name(rd)
            local_name = globaldo_get_projected_member_name(full_name, role_)
            if not context_.has_projection(local_name):
                continue
            lpds.append(context_.get_projection(local_name))
        if lpds:
            systems.append((full_name, lpds))
    return systems


def check_projections(context_, module_):
    """Checks the projection of every global protocol in the module."""
    statuses = []
    pool = [_as_class_lpd(lpd)
            for lpd in context_.get_projections().values()]
    for (name, lpds) in _systems_from_projections(context_, module_):
        report = check_system(lpds, name=name, context_=context_, pool=pool,
                              projected=True)
        for line in report['report']:
            print(line)
        statuses.append(report['status'])
    return statuses


def check_module(context_, module_):
    """Checks every system in the module; prints one report per system."""
    statuses = []
    pool = [_as_class_lpd(lpd)
            for lpd in module_get_localprotocoldecl_children(module_)]
    for (name, lpds) in _systems_of_module(context_, module_):
        if not lpds:
            continue
        report = check_system(lpds, name=name, context_=context_, pool=pool)
        for line in report['report']:
            print(line)
        statuses.append(report['status'])
    return statuses
