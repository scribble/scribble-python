"""Regression tests for the scribblec CLI.

Two gates over the protocol corpus under test/:

  test_validate    -- every .scr file is accepted (exit 0) and prints exactly the
                      diagnostics recorded in test/expected/validate/. Several
                      protocols in test/popl14/WF.scr are deliberate
                      well-formedness violations: scribblec reports those on
                      stdout and still exits 0, so the recorded message is the
                      assertion, not the exit code.
  test_projection  -- every global protocol, projected onto every role, produces
                      exactly the set of local protocols recorded under
                      test/expected/projection/<job>/, byte for byte. A protocol
                      that fails well-formedness check projects no files and
                      prints its diagnostic instead; that is recorded too.

The expected/ tree is generated from the Python 2 reference implementation.
Regenerate it (only after a deliberate behaviour change, and then say so in the
commit message) with

    SCRIBBLE_UPDATE_GOLDENS=1 python3 -m pytest -q

Every job is named <file>__<protocol>_<role> so a failure names its case and
adding a source file does not rename any existing golden directory.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
TESTS = pathlib.Path(__file__).resolve().parent
EXPECTED = TESTS / "expected"
TOOL = REPO / "run" / "scribblec"
GENERATED_PARSER = REPO / "parser" / "src" / "scribble" / "ScribbleParser.py"

ROLE_RE = re.compile(r"\brole\s+([A-Za-z_]\w*)")
MODULE_RE = re.compile(r"\bmodule\s+([\w.]+)\s*;")
PROTO_RE = re.compile(r"\bglobal\s+protocol\s+(\w+)")


def sources():
    """Every .scr file in the corpus that declares a module."""
    return [
        p
        for p in sorted(REPO.glob("test/**/*.scr"))
        # never treat the recorded goldens as corpus input, and leave the
        # deadlock-gate fixtures to test_deadlock.py (its inputs are not
        # protocols whose projection output is worth a golden)
        if "expected" not in p.parts
        and "deadlock" not in p.parts
        and MODULE_RE.search(p.read_text(encoding="latin-1"))
    ]


def jobs():
    """[(name, source, module, protocol, role)] -- one per projection target.

    The name is keyed by the job itself, not by its position in the corpus, so
    adding a source file never renumbers the golden directory of unrelated jobs.
    """
    out = []
    seen = set()
    for src in sources():
        text = src.read_text(encoding="latin-1").replace("\r\n", "\n")
        found = MODULE_RE.search(text)
        assert found is not None
        module = found.group(1)
        for proto_match in PROTO_RE.finditer(text):
            rest = text[proto_match.end():]
            start, end = rest.find("("), rest.find(")", rest.find("("))
            roles = ROLE_RE.findall(rest[start:end])
            for role in dict.fromkeys(roles):
                name = f"{src.stem}__{proto_match.group(1)}__{role}"
                assert name not in seen, f"two jobs share the name {name}"
                seen.add(name)
                out.append((name, src, module, proto_match.group(1), role))
    return out


SOURCES = sources()
JOBS = jobs()


@pytest.fixture(scope="session", autouse=True)
def built_parser():
    if not GENERATED_PARSER.exists():
        subprocess.run(["sh", str(REPO / "run" / "scribblec-build")], cwd=REPO, check=True)


def run_tool(argv, cwd):
    env = dict(os.environ, PYTHON=sys.executable)
    proc = subprocess.run(
        ["sh", str(TOOL)] + [str(a) for a in argv],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def capture(argv, out_dir):
    """Run one job; return a dict relpath -> text (stdout plus produced files)."""
    rc, text = run_tool(argv, cwd=REPO)
    assert rc == 0, f"scribblec {argv} exited {rc}: {text}"
    tree = {"stdout.txt": text}
    if out_dir is not None and out_dir.exists():
        for produced in sorted(out_dir.rglob("*")):
            if produced.is_file():
                rel = produced.relative_to(out_dir).as_posix()
                tree[f"files/{rel}"] = produced.read_text(encoding="utf-8")
    return tree


def compare(golden_dir, tree, label):
    if os.environ.get("SCRIBBLE_UPDATE_GOLDENS"):
        if golden_dir.exists():
            shutil.rmtree(golden_dir)
        for rel, text in tree.items():
            path = golden_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return
    if not golden_dir.exists():
        pytest.fail(f"no golden for {label}: {golden_dir.relative_to(REPO)} is missing")
    expected = {
        p.relative_to(golden_dir).as_posix(): p.read_text(encoding="utf-8")
        for p in golden_dir.rglob("*")
        if p.is_file()
    }
    missing = sorted(set(expected) - set(tree))
    extra = sorted(set(tree) - set(expected))
    if missing or extra:
        pytest.fail(f"{label}: missing={missing} unexpected={extra}")
    for rel in sorted(expected):
        if expected[rel] != tree[rel]:
            diff = subprocess.run(
                ["diff", "-u", str(golden_dir / rel), "-"],
                input=tree[rel],
                text=True,
                capture_output=True,
            ).stdout
            pytest.fail(f"{label}: {rel} differs:\n{diff[:3000]}")


def check_file(path, text):
    """Single-file golden: the diagnostics scribblec prints for one source."""
    if os.environ.get("SCRIBBLE_UPDATE_GOLDENS"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return
    if not path.exists():
        pytest.fail(f"missing golden {path.relative_to(REPO)}; run SCRIBBLE_UPDATE_GOLDENS=1")
    expected = path.read_text(encoding="utf-8")
    if expected != text:
        diff = subprocess.run(
            ["diff", "-u", str(path), "-"], input=text, text=True, capture_output=True
        ).stdout
        pytest.fail(f"{path.name} differs:\n{diff[:3000]}")


@pytest.mark.parametrize("src", SOURCES, ids=lambda p: p.name)
def test_validate(src):
    rel = src.relative_to(REPO)
    rc, out = run_tool([rel], cwd=REPO)
    assert rc == 0, f"scribblec {rel} exited {rc}: {out}"
    # test/popl14/X.scr -> test/expected/validate/popl14/X.scr.txt
    check_file((EXPECTED / "validate" / rel.relative_to("test")).with_suffix(".scr.txt"), out)


@pytest.mark.parametrize("job", JOBS, ids=lambda j: j[0])
def test_projection(job, tmp_path):
    name, src, module, proto, role = job
    out_dir = tmp_path / "out"
    tree = capture(
        [src.relative_to(REPO), "-project", f"{module}.{proto}", role, "-o", out_dir], out_dir
    )
    compare(EXPECTED / "projection" / name, tree, f"project {module}.{proto} to {role}")
