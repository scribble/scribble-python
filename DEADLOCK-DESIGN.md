# Multiparty compatibility checking in `scribblec -deadlock`

Technical description of the gate implemented in `src/scribble/deadlock.py`, the
opt-in flag in `src/scribble/main.py`, and the tests in `test/test_deadlock.py`.

The gate answers one question: **given the local types of the roles of a
protocol, can those roles run to completion under asynchronous, ordered, but
otherwise unconstrained message passing?** It answers by compiling each local
type to a finite labelled transition system, running the machines concurrently
over one FIFO queue per ordered pair of roles, and searching the reachable
configurations for one where progress stops before every role has finished.

Two design commitments shape everything below.

1. **Over-approximate rather than under-approximate, and say so.** Where the
   type syntax admits more than one reading (a choice whose branches begin with
   the same transfer, a channel that fills up, a recursion whose instance
   identity is not decidable), the model takes the reading that produces
   *fewer* verdicts, and records the relaxation as a documented one.
2. **Refuse rather than guess.** Input outside the model (a partial system, a
   projection that addresses a foreign role, a `do` target that does not
   resolve, an exhausted budget) produces `not checked: <reason>`, never `ok`
   and never `deadlock`. A refusal is distinguishable from a pass on both the
   output and the exit status, because a silent `ok` on a partial system is a
   false negative that a CI job would trust.

## 0. Notation

| symbol | meaning |
| --- | --- |
| $R$ | finite set of role names in the system |
| $M_r$ | machine (LTS) compiled from role $r$'s local type |
| $Q_r, q^0_r, \to_r, F_r$ | its states, initial state, transitions, finals |
| $m$ | message key, `name(op1, ..., opn)` from the message signature |
| $C_{pq}$ | FIFO queue from $p$ to $q$, $C_{pq} \in M^{*}$ |
| $\gamma$ | configuration $((q_r)_{r \in R}, (C_{pq})_{p \neq q})$ |
| $B$ | channel bound, `_MAX_CHANNEL = 8` |
| $\kappa(\gamma)$ | deadlock kind: `stuck`, `wait-for`, `unfinished` |

## 1. Machines

Each role's local type compiles to

$$
M_r = (Q_r,\; q^0_r,\; \to_r,\; F_r)
$$

with action alphabet

$$
A = \{\, \mathsf{snd}(m, s) \;|\; m \in M,\ s \in R \,\}
  \;\cup\;
    \{\, \mathsf{rcv}(m, p) \;|\; m \in M,\ p \in R \,\}
  \;\cup\;
    \{\, \varepsilon \,\}
$$

$\mathsf{snd}(m,s)$ is a send of $m$ addressed to $s$; a single node may carry
several destinations (a multicast `m() to B, C;` emits one action per
destination, so the move relation branches). $\mathsf{rcv}(m,p)$ is a receive of
$m$ from $p$. $\varepsilon$ is the silent move that resolves a *local* choice
(§3.1): it changes the role's own state and touches no channel. In the code the
silent action is spelled `skip`.

A state of $M_r$ is not an integer but a **thread tuple** $(i_1, \dots, i_k)$:
one graph index per live parallel branch, with $k = 1$ outside a `par` block.
The tuple is kept in normal form by `_normalise`:

* every index is resolved through continuation cells (`_CONT`) and jump cells
  (`_GOTO`) until it reaches a real node (`_resolve`, which raises
  `recursion body with no interaction` if a cycle of cells closes without ever
  reaching an action, that being a livelock, not a type);
* a `_PAR` head is expanded in place into its branch entries;
* when every thread of a role stands at the same `_JOIN`, the tuple collapses to
  that join's successor, which is how a finished `par` block rejoins.

Normalisation is what makes configurations comparable: two tuples that mean the
same thing have the same representative, so the visited set is exact.

Finishing is a **graph property, not an index comparison**:

$$
q_r \in F_r \iff \textsf{single-head}(q_r) \ \wedge\ \textsf{at-end}(\textsf{head}(q_r))
$$

where `_at_end` resolves the single head to `_END`, and treats a `_SET` head as
finished when *any* of its alternatives ends (the role may be in that branch).
The earlier index comparison declared a role unfinished whenever a parallel
block rejoined through a cell, which made every role-finished module report a
deadlock; the fix is the reason `finished()` and `blocked_roles()` now agree by
construction.

## 2. The system

A configuration is

$$
\gamma = \big( (q_r)_{r \in R},\; (C_{pq})_{p \neq q \in R} \big),
\qquad C_{pq} \in M^{*}
$$

one FIFO per *ordered* pair, so $C_{pq}$ and $C_{qp}$ are independent. The
initial configuration is

$$
\gamma_0 = \big( (q^0_r)_{r \in R},\; (\varepsilon)_{p \neq q} \big)
$$

### 2.1 Transition relation

Three rules, one per action kind. Send appends:

$$
\frac{q_r \xrightarrow{\mathsf{snd}(m,s)} q'_r \qquad |C_{rs}| < B}
     {\gamma \longrightarrow \gamma\big[q_r := q'_r,\; C_{rs} := C_{rs} \cdot m\big]}
$$

Receive pops, and only when the head matches; a mismatch is not a transition at
all (no message can be received out of order):

$$
\frac{q_r \xrightarrow{\mathsf{rcv}(m,p)} q'_r \qquad C_{pr} = m \cdot w}
     {\gamma \longrightarrow \gamma\big[q_r := q'_r,\; C_{pr} := w\big]}
$$

Choice resolves locally:

$$
\frac{q_r \xrightarrow{\varepsilon} q'_r}
     {\gamma \longrightarrow \gamma\big[q_r := q'_r\big]}
$$

A send whose destination has no machine is dropped from the move set, and a send
whose queue is at the bound is suppressed. The first drop is a guard only:
`_check_roles_present` refuses such a system before the search, so with a well
formed input it never fires. The bound is genuinely part of the search, and it
is handled in §4.1.

**Lemma 1 (a decision never blocks).** If $q_r$ is a `_CHOICE` head with a local
(role-decided) choice, then some $\varepsilon$-rule applies, so $\gamma$ is not
stuck. Consequently the search never blames a role for "not having decided
yet": only sends and receives can block, and the classification in §5.1 is
therefore about communication, not about control.

**Lemma 2 ($\varepsilon$ is invisible to channels).** The $\varepsilon$ rule
leaves $(C_{pq})$ untouched, so it cannot change the enablement of any other
role. It follows that the order in which $\varepsilon$-moves are taken does not
affect the set of reachable configurations modulo silent steps.

### 2.2 Termination and progress

$$
F(\gamma) \iff \Big(\bigwedge_{p \neq q} C_{pq} = \varepsilon\Big)
          \wedge \Big(\bigwedge_{r \in R} q_r \in F_r\Big)
$$

$$
\mathsf{enabled}(\gamma) = \emptyset
  \iff \forall r \in R:\ \mathsf{moves}(r, \gamma) = \emptyset
$$

$\gamma$ is a **deadlock** iff it is reachable and

$$
\neg F(\gamma) \ \wedge\ \mathsf{enabled}(\gamma) = \emptyset .
$$

This is the asynchronous-session definition: a queue with traffic nobody will
take is a deadlock even when no single role is waiting for a message that was
never sent, and a role that has run out of protocol while a peer still expects
to talk to it is a deadlock even though nothing is blocked on a receive.

## 3. From syntax to machines

`_Compiler.compile` walks the local-type AST and fills a graph of dict nodes.
Node kinds: `_ACT` (send/receive), `_SKIP` (silent), `_CHOICE`, `_SET`,
`_PAR`, `_JOIN`, `_END`, plus the two resolution cells `_CONT` and `_GOTO`.

### 3.1 Choice: who decides

`_role_decides` inspects the branches. If **every** branch begins with a
receive (looking through nested choices, so a branch that opens with another
choice is not mistaken for one with no receive), the choice is *external*: the
peer decides, and this role learns its branch from the message it receives.
Every other head counts as a local decision: a send, a `skip`, a nested `par`,
a `join`. In that case the role decides itself, and it must decide **now**:
`_choice_moves` emits a `skip` move to every branch entry, including branches
whose first action is not yet enabled.

Committing eagerly is not a convenience. A role that "waits until its first
action becomes enabled" before committing drops exactly the class of failure in
which a role guesses wrong about its peer's branch, which is the asymmetric
choice deadlock (`bad/safety/waitfor` in scribble-java) the gate exists to find.
The look-through in `_role_decides` is the same defect in the opposite
direction: a branch that opens with a nested choice used to look like a branch
with no receive at all, the role was made to commit before the peer had sent
anything, and a live protocol (`good/misc/globals/gchoice/Choice05a`) came back
as a deadlock.

### 3.2 External choice and shared heads

For an external choice each branch is entered by its own first action. When two
branches begin with the *same* transfer, the decider's commitment is internal to
the decider and nothing about it reaches the wire, so from this role's point of
view the two branches are one move with two continuations. `_external_moves`
groups the branches by their first action and merges every group with more than
one member:

$$
\frac{\text{head}(b_1) = \text{head}(b_2) = \mathsf{rcv}(m,p)}
     {\gamma \longrightarrow \gamma\big[q_r := \{\mathsf{entry}(b_1), \mathsf{entry}(b_2)\}\big]}
$$

implemented as a `_SET` node holding the branch entries, one node per distinct
alternative tuple (`_set_node` memoises it on the choice node, so the graph
stays finite). Standing in a set, the role may take any alternative's move
(`_frontier_one` distributes over `alts`) and counts as finished if any
alternative ends (`_at_end`).

The merge is only taken when every branch of the group has a single thread to
put in the set. A branch that opens with a `par` expands to several threads,
there is no single entry to merge, and those branches stay separate, which is
the one place the stricter reading survives.

Taking the branches separately instead lets two roles disagree about the branch
(one in branch 1, the other in branch 2), which is a configuration the protocol
cannot reach, and the search then reports it as a deadlock. That is the shape of
`good/todo/Do04c` in scribble-java once its instantiations are inlined.

The merge is a **relaxation**: every move it adds is a real enabled move at that
configuration (a set-node move requires the actual queue head), so it cannot
invent a deadlock. Its cost is the opposite direction: a deadlock visible only
under the stricter per-branch reading is no longer reported, which is the
intended effect, since that reading is not a behaviour of the protocol.

### 3.3 Parallel

`par { b1 || b2 }` compiles to a `_PAR` with branch entries and a `_JOIN`
carrying the continuation. The role's thread tuple carries one head per live
branch, and the move relation interleaves them (`_frontier` picks one live
thread and advances it). The join is taken when all branches reach it, which is
the collapse rule in `_normalise`.

### 3.4 Recursion as a fixpoint

`rec X { ... continue X; }` becomes a continuation cell whose target is the body
entry, so `continue` is a jump to a node that already exists. Nothing is
unrolled, so a cyclic type gives a cyclic graph.

`do P(A as B)` instantiates another local type by inlining. Inlining a
self-recursive protocol would unroll indefinitely, so instantiation is keyed:

$$
\mathsf{key} = \big(\mathsf{site}(\texttt{do}),\ \mathsf{sub}\big),
\qquad
\mathsf{sub} : \text{callee role} \rightharpoonup \text{caller role}
$$

`_site_of` identifies the syntactic `do` node (a side table keyed by object
identity, since the same protocol text compiled twice is a different site), and
$\mathsf{sub}$ is the role substitution built by `_do_substitution`. A second
entry through the same site with the same substitution is the **same state**, so
the edge closes and the recursion becomes a fixpoint rather than a sequence of
unfoldings. That is the coinductive reading of recursion the other Scribble
checkers implement, and it is what makes the state space finite with no depth
bound.

Two cases are refused rather than approximated:

* a repeated key whose recorded continuation differs from the current one
  (`recursive instantiation of … whose continuation is not in tail position`);
  reusing the first continuation would silently move behaviour between
  machines;
* more than `_MAX_INSTANCES = 4` distinct substitutions at one site
  (`… with unboundedly many role renamings`), which is where the instance
  abstraction stops being finite.

Role substitution is read **positionally**, because position is what the source
says: one role instantiation per role of the callee, in declaration order. The
projection-derived table is consulted only when the two lists do not line up,
and disagreement there is refused (`conflicting instantiations of …`).

## 4. The search

`explore` is a breadth-first traversal of the reachable configurations.

* `visited` is keyed by the **normalised** configuration: `key()` rebuilds the
  channel map in sorted pair order, so two dicts with the same content are one
  key, and thread tuples are already normalised.
* The queue is a list walked by index. Each configuration is expanded once, so
  the first dead configuration found has a **shortest** run reaching it; the
  trace is a shortest counterexample, not an arbitrary one.
* A parent map plus a per-configuration action map reconstructs the trace by
  walking back from the dead configuration and reversing.
* `states` counts discovered configurations, `transitions` counts moves
  enumerated from expanded ones. Both are reported, so two runs can be compared.

Determinism: roles are visited in sorted order and moves in graph order, so the
same input always yields the same trace.

### 4.1 Budgets

$$
|\text{reachable}| \le \texttt{\_MAX\_STATES} = 200000,
\qquad
|C_{pq}| \le B = 8 .
$$

Exhausting the state budget yields `not checked: state bound 200000 reached`.

The channel bound needs care. Suppressing a send removes a move, and a removed
move can make a configuration stuck that would not be stuck on a longer queue.
That is a **false positive**, and it is reachable in practice: a protocol with
nine sends outstanding on one channel before the receiver can drain it blocks at
the ninth. `chan9.scr` (in `test/deadlock/`) is exactly that protocol, three
roles, nine messages from A to B issued before C is asked for the message B
actually waits on:

```
$ scribblec test/deadlock/chan9.scr -deadlock      # _MAX_CHANNEL = 8
[Deadlock] chan9: not checked: channel bound 8 reached on A -> B

$ # same file, same search, model bound raised to 64
[Deadlock] chan9: ok (23 states, 22 transitions)
```

So `explore` distinguishes the two reasons a configuration can be stuck.
`bound_hit` asks, for each role with no moves, whether some send at its head
targets a role whose queue is at the bound. If one does, the configuration is
refused:

$$
\mathsf{stuck}(\gamma) \ \wedge\ \exists r,s:\
  \textsf{head}(q_r) = \mathsf{snd}(m,s) \ \wedge\ |C_{rs}| = B
  \;\Longrightarrow\; \texttt{not checked}
$$

The refusal can hide a genuine deadlock in that same configuration (a false
negative), which is the accepted direction; it cannot invent one.

`_describe` also distinguishes the two reasons a send can be unavailable ("no
such role is in the system" versus "the channel is full"), because a misleading
reason line is a defect of its own.

## 5. Verdicts

`check_system` prints one verdict per system:

```
[Deadlock] <system>: ok (N states, M transitions)
[Deadlock] <system>: deadlock (<kind>)
[Deadlock]   <role>: <reason>            (one line per blocked role)
[Deadlock]   shortest trace (N steps) over S states:
[Deadlock]     <role>: <action>
[Deadlock] <system>: not checked: <reason>
```

and the exit status is part of the contract:

$$
\text{exit} =
\begin{cases}
1 & \text{verdict is } \texttt{deadlock}(\cdot) \\
0 & \text{verdict is } \texttt{ok} \text{ or } \texttt{not checked}:\ \cdot
\end{cases}
$$

A gate that reports a deadlock and exits 0 cannot fail a build, so both branches
are pinned by tests.

### 5.1 Classification

$$
\kappa(\gamma) =
\begin{cases}
\texttt{stuck} & \exists r:\ \textit{reason}(r) \ni \text{``is at the head of that channel''} \\
\texttt{unfinished} & \exists r:\ \textit{reason}(r) \text{ starts with \texttt{finished}} \\
\texttt{wait-for} & \text{otherwise}
\end{cases}
$$

in that precedence. The three shapes have different causes and different fixes:

* `stuck`: the head of a queue is a message no one wants. The parties disagree
  about the order of traffic on one channel (classic: `bad/safety/stuckmsg`).
* `unfinished`: a role has run out of protocol while a peer still expects to
  talk to it (classic: an early `end` on one side).
* `wait-for`: a circular wait. Every role is waiting for a message that has not
  been sent, none of them can send, which is the shape a hand-written set of
  local types most often breaks (`bad/safety/waitfor`).

The reason lines come from `_describe`, which reads the head node and the queue:
`waiting for m from P, which has not been sent`,
`waiting for m from P, but 'x' is at the head of that channel`,
`wanted to send m to Q, but no such role is in the system`,
`wanted to send m to Q, but the channel is full (8 messages, which is the model
bound)`, `a choice none of whose branches can start`, and, when the role stands
in a merged set, `a choice of N branches, none of which can start`.

## 6. Refusals

Every precondition runs before the search, except the two budgets, so a refusal
is decided from the input, not from a partial exploration.

| condition | where | message |
| --- | --- | --- |
| a machine addresses a role outside $R$ (projections only) | `_check_role_closure` | `the projection for r talks to s, which is not a role of the protocol` |
| a machine addresses a role the module has no local type for | `_check_roles_present` | `role s is addressed by r but has no local type in this module` |
| two local types for one role | `check_system` | `two local types for role r` |
| `do` target does not resolve | `_compile_do` | `instantiation of unknown local protocol <name>` |
| same site, different continuation | `_compile_do` | `recursive instantiation of P whose continuation is not in tail position` |
| more than 4 substitutions at one site | `_compile_do` | `recursive instantiation of P with unboundedly many role renamings` |
| projection tables disagree | `_do_substitution` | `conflicting instantiations of P` |
| a jump cycle with no action in it | `_resolve` | `recursion body with no interaction` |
| state budget exhausted | `explore` | `state bound 200000 reached` |
| a send suppressed by the channel bound | `explore` | `channel bound 8 reached on r -> s` |

`_check_roles_present` deserves the reasoning. A module may declare local types
for $A$ only, while $A$'s type addresses $B$. The system is then *partial*: $B$
never runs, so every send to it blocks and the search would report a deadlock
that the file does not have. Refusing is the only honest option, and it is why
`Import13_Import13_A.scr` and `Pack13_Pack13_C.scr` report
`not checked` rather than a deadlock. The same applies to a projection set:
`_check_role_closure` refuses a projection that addresses a role its global
protocol does not have, because the deadlock it would find is a deadlock in our
reading of the file, not in the file.

## 7. Where it runs

`main.py` calls the gate only when `-deadlock` (or `-deadlock-export`) is given,
immediately after `_check_reachability`:

```python
_check_reachability(context_)

if args[_DEADLOCK]:
    deadlock.set_export_dir(args[_DEADLOCK_EXPORT])
    module_ = context_.get_module(module_get_full_name(module_))
    statuses = deadlock.check_projections(context_, module_)
    statuses += deadlock.check_module(context_, module_)
    if deadlock.DEADLOCK in statuses:
        sys.exit(1)
```

Systems come from two sources:

* `check_projections`: for each global protocol, the set of its EPP projections
  is one system, which is the composition the global type prescribes and the
  input a global-first checker works on;
* `check_module`: the module's own local protocol declarations, grouped by
  *roots* (`_root_localprotocoldecls` drops every type that some `do`
  instantiates, so the callee is part of the caller's system rather than a
  system of its own; a mutually recursive module has no root, and then the whole
  module is the system).

Being opt-in keeps every non-deadlock golden byte-identical, which matters
because those goldens are the porting oracle.

## 8. Guarantees, stated precisely

| claim | status |
| --- | --- |
| no false negatives from the search itself | holds: the search is exact on the model |
| no false positives from the choice merge | holds: every merged move requires real queue content |
| no false positives from the channel bound | holds since the bound-blocked case is refused |
| no false negatives from the channel bound | **does not hold**: a deadlock in a bound-blocked configuration is refused, not reported |
| liveness / fairness | **not checked**: a cycle of sends that never terminates reports `ok` |
| progress beyond "stuck state reachability" | **not checked**: no fairness assumption is modelled |
| unbounded recursion | refused, not modelled |

The liveness gap is the clearest scope limit: the gate is a safety check
(something bad is reachable), not a termination check (something good is
eventually reached). `bad/liveness/{messagelive,roleprog}` in scribble-java
therefore report `ok`.

## 9. Evidence

Regression suite: `pytest -q` gives 73 passed, 9 fixtures in `test/deadlock/`
covering a three-party cycle, an asymmetric choice, a stuck queue and its live
sibling, mutual recursion in both variants, positional and `as`-pair `do`
substitution, a partial system, a bound-blocked channel, plus opt-in and export
behaviour.

Corpus sweep over scribble-java's test resources (`bad/` and `good/`, 416
files): 196 verdict lines, of which 188 `ok`, 8 `not checked`, 0 `deadlock`,
plus 4 tracebacks upstream of the gate (2 `KeyError` in
`globaldo.project → context.get_visible_global`, 2 `RecursionError` projecting
`grecursion` fixtures). The zero deadlock count is **not** a soundness claim:
scribble-java's `bad/safety` and `bad/liveness` fixtures use numeric message
operators (`1() from A to B;`) that our grammar rejects, so those files never
reach the gate. Sensitivity is carried by `test/deadlock/`.

## 10. Open items

* **Recursion with no interaction** is currently a refusal
  (`recursion body with no interaction`, from `_resolve`). It is a divergence,
  not a stuck state, so the honest verdict is a fourth kind rather than a
  refusal; either way it must not read as "fine".
* **Non-tail recursion** (`continuation not in tail position`) needs a call and
  return stack inside the configuration instead of a refusal. The instance key
  already carries the site and the substitution; the missing piece is the return
  continuation as part of the key.
* **Liveness**: a fair-scheduling or strongly-connected-component check would
  turn "no stuck state" into "every role can finish", which is what the
  multiparty-compatibility literature actually proves.
* **Channel bound**: raising $B$ only moves the boundary. The real fix is to
  make the queue abstract (a multiset with a bound derived from the protocol's
  message alphabet) so the refusal disappears instead of being pushed out.
* **Set narrowing**: `_SET` keeps every alternative alive, which is what makes
  the merge sound; narrowing it by which branches are still consistent with the
  wire would reduce the state space without changing verdicts.
