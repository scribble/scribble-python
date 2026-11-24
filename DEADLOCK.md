# Deadlock checking for scribble-python

This note records what scribble-python does and does not guarantee about a
protocol, the multiparty-compatibility check added here on branch `py3`
(`src/scribble/deadlock.py`), how it compares with scribble-java and the other
tools in the area, and what is left to do. Nothing in this working tree is
committed; PR #7 carries only the Python 3 port.

## 1. What upstream scribble-python guarantees

The published tool checks a protocol a priori, in three stages, and none of them
is a compatibility or deadlock check:

| stage | code | catches |
|---|---|---|
| well-formedness (§4.6.1–§4.6.10) | `src/scribble/visit/wellformednesschecker.py`, `visit/context.py` | unconnected roles, choice-subject rules, linearity of recursion, choice merge (`Bad choice operator`), global escape, etc. |
| endpoint projection (EPP) | `src/scribble/visit/projector.py` | a global type that does not project (roles that do not take part in a choice, `.` in choices) |
| local reachability | `src/scribble/ast/local/localinteractionsequence.py` | a local type whose next interaction is never enabled (`Bad sequence: …`) |

All three are local, inductive conditions on the syntax of one protocol. None of
them builds the product of the role behaviours, so none of them can see a
protocol in which every role is individually well formed and yet the roles
block each other. Those are exactly the protocols Scribble's own `bad/safety`
and `bad/liveness` test corpora are made of. `scribblec` reports the three
stages and exits 0 regardless.

## 2. The check

`scribblec -deadlock file.scr` (and `-deadlock-export <dir>` for graphs) runs
after the existing checks, so without the flag output is byte-identical to
upstream.

Model:

* every role's local type is compiled to a small labelled transition system:
  nodes are `act` (send/recv with one message), `choice`, `par`/`join`,
  `cont`/`goto` (recursion), `set` (see §4), `end`;
* the roles run concurrently, one FIFO queue per ordered pair of roles
  (asynchronous, which is what EPP assumes);
* a global type contributes the systems of its projections, not only the
  declared local protocols, and those are checked first, matching
  scribble-java's global-first path;
* the product is searched breadth first. A state is a deadlock when at least
  one role has no enabled action and is not finished; the report names the
  role, says what it was waiting for or sending, and prints the shortest trace
  to the state.

Decisions worth recording:

* **Internal vs external choice is inferred from the branches**, not from
  syntax: a choice whose branches begin with a receive (or with a `do` that
  inlines to one) is decided by a peer, so this role enters a branch because a
  message arrived. `_role_decides` resolves this through nested choices.
* **`do` is instantiated by call site plus role substitution**
  (`_site_of`, keyed on `(_site_of(item), tuple(sorted(sub.items())))`), so a
  self-instantiating protocol closes as a back edge instead of unfolding
  forever; only substitution growth is bounded (`_MAX_INSTANCES = 4`).
* **Finished is a graph property, not an index.** A role is finished when its
  head resolves (through `cont`/`goto`/`join`) to an `end` node. The first
  implementation compared the head index with the index the end node was
  created at, which is false for any role whose parallel branches join into the
  end through a continuation; completed protocols were being reported as
  deadlocks.
* **Projections are closed:** if the local types are the projection of one
  global type and a projection addresses a role outside that protocol, the
  system is refused ("not checked: the projection for A talks to D, which is
  not a role of the protocol") rather than reported. A deadlock found by
  reading such a file is a deadlock in our reading, not in the file.

## 3. What it finds, next to scribble-java

scribble-java (`scribble-dist-0.5.1-SNAPSHOT`, built here) enumerates the same
product but reports *violations* with state numbers, and distinguishes
`Stuck messages` from `wait-for` cycles. On the fixtures both tools can read
the verdicts agree:

| fixture | scribble-java | this gate |
|---|---|---|
| `bad/safety/waitfor/twoparty/Test01` | violation, state 91, wait-for [[A,B]] | deadlock (wait-for) |
| `bad/safety/stuckmsg/twoparty/Test04` | violation, state 37, `Stuck messages: {A=B?2()}` | deadlock (stuck) |
| `bad/safety/waitfor/threeparty/Test03` | violation, state 38, wait-for [[B,C]] | deadlock (wait-for), same class |
| `good/wfchoice/enabling/twoparty/Test02` | clean | ok |
| `good/todo/Do04c`, `Do12b`, `Do18` | clean | ok |
| `good/misc/globals/gchoice/Choice05a` | clean | ok |

Asymmetries, both directions:

* scribble-java refuses a module that declares only local protocols
  (`line 3:0 missing EOF at 'local'`); this front end accepts it, and the gate
  checks it.
* our well-formedness is *stronger* than java's `wfchoice` on one shape: a
  global choice whose branches a peer cannot tell apart is rejected outright
  (`Bad choice operator: .m1`) where java proceeds and reports the resulting
  stuck state.
* `good/misc/imports/Import13`, `Import14` and `good/reach/globals/gdo/Test06a`
  were first refused by the closure rule above, which looked like a projector
  defect: a caller's `do` appeared to keep addressing a role the caller never
  talks to. It was the gate reading the projector's output wrong, not the
  projector; with that fixed (§5) all three report `ok`.
* scribble-go was considered as a third leg and dropped: it is a code
  generator plus runtime library, with no static check (`grep -i
  'deadlock|safety|liveness|validat'` over the tree finds nothing).

## 4. The defect that took the longest: choice branches that inline to the same head

`good/todo/Do04c` in java's corpus is clean, and the first version of the gate
called it a deadlock. The protocol decides a choice at `A`; one branch is a
single transfer, the other is a `do` whose body is two transfers. Projecting
and inlining gives `B` a choice whose two branches both begin with the same
receive. Nothing about `A`'s commitment travels on the wire, so `B` cannot tell
the branches apart; treating them as two separate moves lets the search put
`A` in branch one and `B` in branch two, a state the protocol cannot reach,
where `B` waits for a message that will never come.

The shape survives well-formedness because `Bad choice operator` does not look
through an instantiation.

The fix is the one nuscr and scribble-java both implement in their merge
algorithms: *merge first*. Branches that share their first action become one
move into a `set` node holding the branch entries (`_external_moves`,
`_set_node`). A role standing in a set may take any branch's moves, and counts
as finished if any branch ends (`_at_end`). Two properties follow:

* the false deadlock on `Do04c` and on the reduced fixtures `dl/corr.scr`,
  `dl/corr1.scr` (one instantiation), `dl/corr2.scr` (two) disappears;
* a *genuine* asymmetric-choice deadlock still reports, because there the peer
  must commit to an action it sends and can pick the wrong one. `dl/stuckmsg.scr`
  (java's `Test04` transcribed as two local types, each `choice at B`) still
  gives `deadlock (stuck)`.

The reading is deliberately an over-approximation: once a role is in a set its
branches are not narrowed when a later message arrives, so a deadlock that only
appears after that narrowing can be missed. Over-approximating can lose a
finding, never invent one.

## 5. The second defect: role instantiation read off the wrong list

The same inlining step, a different loss. A `do` in a projected local type
carries one role instantiation per role of the callee, in the callee's
declaration order, spelled with the *caller's* role names:

```
do Pack13_C(A, B)          # caller  A's projection, callee declares C, D
do Pack13_D(...)           # caller  B's projection
```

Only where the source wrote the correspondence out, `do X(A as D)`, does each
pair carry its second half. The first version of `_do_substitution` read the
substitution from those explicit pairs alone and, as a fallback, from a table
built by walking every projection and recording *callee role → caller role* per
callee member. Both sources are wrong for the plain form:

* the explicit pairs are absent, so nothing binds `C` to `A` or `D` to `B`;
* the projection table collapses frames. One projection member per (protocol,
  role) means `Pack13_C`'s `do` to `Import13Aux_A` and `Import13_A`'s `do` to
  the same member are recorded under one key, once as `A -> C` (Pack13's frame)
  and once as `A -> A` (Import13's). The table has no single reading, so
  `_renames_of` marked the instantiation ambiguous, and the closure check
  refused the system: `not checked: projection of ...A addresses role D`.

The callee's role declaration list is the authority the source actually
provides. `_do_substitution` now zips `target_.get_roledecllist().roledecls`
with `item.get_roleinstantiations()` positionally whenever the two lists are
the same length (`_role` maps the caller-side name through the frame's own
renamings), and consults the projection table only when they are not. That is
the whole fix; `callee.get(...)` still folds the callee's own aliases onto the
names, and an explicit `as` pair now agrees with the positional reading
instead of overriding it.

Effect: `Import13`, `Import14` and `Test06a.Bar` go from `not checked` to
verdicts (`ok (5 states, 5 transitions)`, `ok (5, 5)`, `ok (18, 32)`). It is
worth being precise about what was *not* broken: the projector was right all
along, the gate was reading its output wrong. `dl/dumpproj.py` prints, for one
file, each projection's role declarations and every `LocalDo` with its
instantiations, which is what settled it.

## 6. The four steps

1. **Recursion as a fixpoint.** Instances are keyed by call site and role
   substitution and closed as back edges, with no unfolding bound; only
   substitution growth is capped. `dl/selfrec_ok.scr` (mutual self-instantiation
   that terminates) reports `ok` in 12 states; `dl/selfrec_dead.scr` reports
   `deadlock (wait-for)`.
2. **Breadth-first with a shortest trace.** `explore` returns the state at
   which the search stopped and the path to it; the report prints
   `shortest trace (N steps) over S states` with one line per action.
3. **Status vocabulary.** Every verdict is one of `ok (S states, T
   transitions)`, `deadlock (wait-for)`, `deadlock (stuck)` (a role is blocked
   with messages still in flight, or waiting for a message that is at the head
   of its queue under a different label), or `not checked: <reason>`. The
   header carries the kind: `[Deadlock] <system>: deadlock (<kind>)`.
4. **Export.** `-deadlock-export <dir>` implies `-deadlock` and writes one DOT
   graph per reported system (states, transitions, sends dashed, the trace
   highlighted), capped at `_MAX_EXPORT_STATES = 5000`. Renders with
   `dot -Tsvg`.

## 7. Adjacent tools and what to take from them

Surveyed: mpsTK (Scala, mCRL2 back end), nuscr (Rust, Scribble + refinement
types), STMonitor (runtime monitors from Scribble), Pabble (parameterised
protocols), HasChor, Choral (choreographic programming languages), CSA
(communications safety analysis). Ranked by what fixes a known weakness here:

1. **mCRL2-style recursion as a fixpoint plus `pbessolve -w`.** mpsTK compiles
   the protocol to an mCRL2 process (`lps2lts`, `lps2pbes`) and lets the model
   checker do the search, which gives shortest counterexamples and, more
   importantly, *liveness* properties (does every pending message eventually
   get consumed, can a role starve) as separate specifications rather than as
   one deadlock predicate. This gate searches for deadlock only.
2. **Merge first, and name the role in the diagnosis.** nuscr's merge reports
   which role caused the conflict (`#137`, merge across unparameterised
   recursion) and merges at the type level instead of enumerating first. Our
   §4 fix is a runtime version of the same idea; doing it on types would give
   better messages and prune the product before it is built.
3. **Liveness and never-termination as their own properties.** java has
   `bad/liveness/{messagelive,roleprog}`; this gate covers safety
   (stuck/wait-for) and would report a protocol that can loop forever as `ok`,
   since a cycle in the state graph is not a deadlock.

Pabble's parameterised protocols and Choral/HasChor's choreographic languages
are outside the scope of a checker for the Scribble surface syntax; CSA is a
different calculus. STMonitor is complementary: it turns the same EPP output
into runtime monitors, which is the second half of the story this gate tells
statically.

## 8. Running it

```
sh run/scribblec file.scr -deadlock
sh run/scribblec -deadlock-export /tmp/dots file.scr   # writes *.dot
sh run/scribblec -ip <resource-dir> -deadlock <file>.scr
```

Fixtures used during development live in `~/.hermes/cache/scratch/dl/`
(`corr{1,2,3}`, `dochain`, `selfrec_{ok,dead}`, `stuckmsg{,_ok}`, `circle`,
`ours_waitfor2`, `shapes`, `enabling_global`, `wf_global`, `stuck_global`), plus
`probe.py`, `dbg.py` and `dumpproj.py` for printing projections and
machines. The gate has its own regression suite: fixtures in `test/deadlock/`
(good, deadlocking and partial systems) checked by `test/test_deadlock.py`;
`test/test_scribblec.py` skips that directory when it walks the corpus, so the
gate fixtures need no projection goldens. The whole suite is green (72 tests,
`pytest -q`), and the golden files are unchanged, which is the regression oracle
for the port itself.

Verdicts on the import fixtures, after the `do` fix in §5:

| file | verdict |
| --- | --- |
| `good/misc/imports/pack1/Pack13.scr` | `ok (3 states, 2 transitions)` |
| `good/misc/imports/Import13_Import13_A.scr` | `not checked: role B is addressed by A but has no local type in this module` |
| `good/misc/imports/Import13_Import13Aux_A.scr` | same refusal |
| `good/misc/imports/pack1/Pack13_Pack13_C.scr` | `not checked: role D is addressed by C ...` |

That is the honest answer for these files rather than the `ok` claimed in an
earlier draft: `Import13_Import13_A` is the projection of `Import13` onto role
`A`, so it holds one role's local type and names its partners without defining
them. A single-machine "system" is partial, and the gate refuses it instead of
reporting a deadlock it cannot see (`_check_roles_present`). `Import16.scr` and
`good/syntax/disamb/imports/Import04.scr` never reach the gate: they raise
`KeyError` inside `globaldo.project` -> `context.get_visible_global`, a
projector defect that predates this work.

## 8.1 Corpus sweep

`-deadlock` over every `.scr` in the java test resources (416 files, `-ip`
set to the resource root):

| | count |
| --- | --- |
| files | 416 |
| `[Deadlock]` verdict lines | 196 |
| `ok (N states, M transitions)` | 188 |
| `not checked:` | 8 |
| `deadlock (...)` | **0** |
| tracebacks | 4 |

The zero is not evidence that the gate is sound over that corpus: scribble-java
writes numeric message operators (`1() from A to B;`), which our grammar rejects
before any check runs (`no viable alternative at character '1'`, then
`Bad choice operator: .EMPTY_MESSAGE_OP`). Every `bad/safety` and `bad/liveness`
fixture is therefore invisible to the gate, and deadlock sensitivity is covered
by `test/deadlock/` alone.

The 8 refusals, by reason:

| reason | files |
| --- | --- |
| `role … is addressed by … but has no local type in this module` | `Import13_Import13_A`, `Import13_Import13Aux_A`, `Pack13_Pack13_C` |
| `recursion body with no interaction` | `GProtocolDecl3a`, `GProtocolDecl3b`, `Do13a` |
| `recursive instantiation of … whose continuation is not in tail position` | `Import02.Foo`, `Do04b.Do4b` |

The 4 tracebacks are all upstream of the gate: `KeyError` in
`globaldo.project -> context.get_visible_global` (`Import16`, `Import04`) and
`RecursionError` projecting the grecursion fixtures (`Test04a`, `Test04b`).

## 9. Open items

* Narrowing a `set` when a later message arrives (see §4) would remove the
  over-approximation.
* Liveness (`messagelive`, `roleprog`) is not checked; see §7.1 and §7.3.
* `recursion body with no interaction` is a refusal, not a verdict, but an
  infinite recursion that never sends a message is a real livelock; reporting
  it as `deadlock (stuck)` would be more useful than refusing.
* A recursive instantiation outside tail position is refused (a call in the
  middle of a body would need the machine to return to a saved continuation);
  the fix is a call/return stack in the state, not an unbounded instance table.
* No CI: upstream Actions is not enabled for the fork, so the pytest workflow
  in `.github/workflows/tests.yml` has never run in the cloud.
* Four `good/` files still fail parsing (grecursion/import shapes) and five are
  rejected at well-formedness although java accepts them; nine
  `bad/syntax/disamb/*` are silent (the grammar rejects java-only syntax before
  any check runs). All three are parser/checker gaps upstream of the gate.

Two things are worth recording because they cost time and will cost it again:

* **Never run `run/scribblec-build` and `pytest` in one shell job.** The build
  regenerates `parser/src/scribble/ScribbleParser.py`; an interpreter that
  imports it mid-write raises `SyntaxError: expected ':'` around line 3857 and
  the suite reports `1 failed, 58 passed` on a file that is fine. Build first,
  then test in a separate invocation.
* **`scribblec` exits 0 on validation errors** (projection, well-formedness and
  this gate), so a test asserts on the message text, not the exit status. This
  gate has one deliberate exception: a `deadlock (...)` verdict exits **1**, so
  `-deadlock` can gate a build; `ok` and `not checked:` exit 0.
* **A `do` target is a flat run of name tokens, not one name.** A `do` node
  reads `(LOCALDO __1 EMPTY_ARGUMENT_LIST (ROLEINSTANTIATIONLIST ...) good misc
  pack1 P A)`. `CommonTree.getText()` returns only the root token (`LOCALDO`),
  so a scan of the node text sees nothing; `globaldo.get_target` returns only
  the first segment (`good`), which is what made the gate ask for a local
  protocol called `good`. Read the name with
  `localdo.get_target_name_children(tree)` and join with dots.
* **Node types are strings.** `constants.LOCAL_PROTOCOL_DECL_NODE_TYPE` is
  `'LOCALPROTOCOLDECL'`, while `node.getType()` returns an int, so
  `node.getType() == constants.X` is silently false for every constant. Use
  `scrib_util.get_node_type(node)`, which is what the rest of the port does.
* **`Context.get_member` raises `KeyError`** on a miss; it does not return
  `None`. Guard it, and try the module alias as well when the target starts
  with an `import ... as X` alias.

Resolved since the first draft: the projector renaming defect (§5) and
`-deadlock-export` with no argument, which now reports
`Bad argument flag: -deadlock-export requires a directory` instead of raising
`StopIteration` from `next(it)`.
