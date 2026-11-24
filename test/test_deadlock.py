"""Regression tests for the multiparty-compatibility (deadlock) gate.

`scribblec -deadlock` compiles every role's local type to an LTS, runs the roles
concurrently over one FIFO per ordered role pair, and searches the reachable
states for a state that is blocked while some role has not finished.  The
verdict is printed as

    [Deadlock] <system>: ok (N states, M transitions)
    [Deadlock] <system>: deadlock (<kind>)      kind in stuck|wait-for|unfinished
    [Deadlock] <system>: not checked: <reason>

`not checked` is a refusal, not a pass: the input is outside what the gate can
speak about (an incomplete system, a role addressed by no local type, a `do`
whose target cannot be resolved).  Keeping refusals distinct from `ok` matters:
a silent `ok` on a partial system would be a false negative.

The fixtures in test/deadlock/ are excluded from the golden corpus in
test_scribblec.py: they are gate inputs, not projection or validation goldens.

Exit status is part of the contract: a deadlock verdict exits 1 so the gate can
fail a build, while `ok` and the refusals exit 0.  The assertions below pin both,
because a gate that reports a deadlock and exits 0 cannot be used in CI.
"""
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
FIXTURES = pathlib.Path(__file__).resolve().parent / "deadlock"
TOOL = REPO / "run" / "scribblec"


def run_deadlock(source):
    """(exit status, output) for one fixture, gate enabled."""
    proc = subprocess.run(
        ["sh", str(TOOL), str(source), "-deadlock"],
        cwd=REPO,
        env={"PYTHON": sys.executable, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert proc.returncode in (0, 1), (
        f"scribblec {source.name} -deadlock crashed ({proc.returncode}): "
        f"{proc.stdout}{proc.stderr}"
    )
    return proc.returncode, proc.stdout + proc.stderr


def verdicts(text):
    """{system: verdict} for every [Deadlock] verdict line in the output."""
    out = {}
    for line in text.splitlines():
        if not line.startswith("[Deadlock] "):
            continue
        body = line[len("[Deadlock] "):]
        system, sep, rest = body.partition(": ")
        if sep:
            out[system] = rest
    return out


# (fixture, system, expected verdict) -- one row per system the gate reports.
CASES = [
    # A three-party cycle: every send is enabled but the system closes on
    # itself, so the state is blocked with all roles unfinished.
    ("circle.scr", "circle", "deadlock (wait-for)"),
    # A two-party choice where both parties pick the branch that leaves the
    # other blocked.
    ("ours_waitfor2.scr", "ours_waitfor2", "deadlock (wait-for)"),
    # A message left at the head of a FIFO that peer will never receive.
    ("stuckmsg.scr", "stuckmsg", "deadlock (stuck)"),
    # ... and its well-behaved sibling.
    ("stuckmsg_ok.scr", "stuckmsg_ok", "ok (10 states, 10 transitions)"),
    # Mutual recursion: the deadlocking and the live variant differ only in
    # which branch the recursion re-enters, which is what the call-site keyed
    # `do` instance is there to distinguish.
    ("selfrec_dead.scr", "selfrec_dead", "deadlock (wait-for)"),
    ("selfrec_ok.scr", "selfrec_ok", "ok (12 states, 12 transitions)"),
    # Role renaming across a `do`, written positionally and with `as` pairs.
    ("dosubst.scr", "dosubst.Main", "ok (5 states, 4 transitions)"),
    ("dosubst.scr", "dosubst.Main2", "ok (5 states, 4 transitions)"),
    ("dosubst.scr", "dosubst.Sub", "ok (5 states, 4 transitions)"),
    # A single projection of a two-role system: refused, never reported.
    ("partial.scr", "partial",
     "not checked: role B is addressed by A but has no local type in this "
     "module"),
    # Nine sends outstanding on one FIFO: the channel bound (8) stops the
    # ninth, so the state is blocked only because of the model's bound, not
    # because of the protocol.  The gate must refuse, not report a deadlock.
    ("chan9.scr", "chan9", "not checked: channel bound 8 reached on A -> B"),
]


@pytest.mark.parametrize("name,system,expected", CASES,
                         ids=[f"{name}:{system}" for name, system, _ in CASES])
def test_deadlock_verdict(name, system, expected):
    status, text = run_deadlock(FIXTURES / name)
    got = verdicts(text)
    assert system in got, f"{name}: no [Deadlock] verdict for {system}: {got}"
    assert got[system] == expected
    # a reported deadlock fails the run; a clean or refused system does not
    assert status == (1 if expected.startswith("deadlock (") else 0), text


def test_no_deadlock_output_without_the_flag():
    """The gate is opt-in: a plain run stays byte-identical to the old CLI."""
    proc = subprocess.run(
        ["sh", str(TOOL), str(FIXTURES / "stuckmsg.scr")],
        cwd=REPO,
        env={"PYTHON": sys.executable, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "[Deadlock]" not in proc.stdout + proc.stderr


def test_export_writes_one_dot_per_system(tmp_path):
    """-deadlock-export implies -deadlock and drops a DOT graph per system."""
    proc = subprocess.run(
        ["sh", str(TOOL), "-deadlock-export", str(tmp_path),
         str(FIXTURES / "circle.scr")],
        cwd=REPO,
        env={"PYTHON": sys.executable, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    # circle.scr deadlocks, so the run reports it and exits 1
    assert proc.returncode == 1, proc.stdout + proc.stderr
    produced = sorted(p.name for p in tmp_path.iterdir())
    assert produced == ["circle.dot"], produced
    # the graph is the role LTS, not the deadlock trace: one node per state,
    # sends as dashed edges, terminals doubled.  The verdict is on stdout.
    dot = (tmp_path / "circle.dot").read_text()
    assert dot.startswith('digraph "circle"')
    assert '-> "s1"' in dot or '-> s1' in dot
    assert "send " in dot
    assert "shape=doublecircle" in dot


def test_export_flag_requires_a_directory():
    proc = subprocess.run(
        ["sh", str(TOOL), str(FIXTURES / "circle.scr"), "-deadlock-export"],
        cwd=REPO,
        env={"PYTHON": sys.executable, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )
    text = proc.stdout + proc.stderr
    assert "-deadlock-export requires a directory" in text
