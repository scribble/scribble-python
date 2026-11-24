scribble-python
===============

scribblec is a command line tool for validating the well-formedness of Scribble
global protocols and performing the projection to local protocols.

This repository is a fork of https://github.com/scribble/scribble-python that
has been migrated from Python 2 to Python 3 (see "Migration notes" below).
It has been tested on Debian Linux.


Building the tool
-----------------

- Requirements: Java 7 or later, Python 3.9 or later

- From the scribble-python base directory:

  run/scribblec-build

  This runs the bundled ANTLR 3.5.3 tool (antlr/antlr-3.5.3-complete.jar) over
  src/scribble/Scribble.g, writing the generated lexer and parser to parser/.


Running the tool
----------------

- Requirements: Python 3.9 or later

We use the test/popl14/Negotiation1.scr Scribble source file as an example.

- To validate the well-formedness of all global protocols, from the
  scribble-python base directory:

  run/scribblec test/popl14/Negotiation1.scr

- To additionally project the "Negotiate" global protocol in this file to the
  local protocol for role "Consumer", to the output directory "output":

  run/scribblec test/popl14/Negotiation1.scr -project popl14.Negotiation1.Negotiate Consumer -o output

- The interpreter used to run the tool defaults to python3 and can be
  overridden with the PYTHON environment variable:

  PYTHON=python3.12 run/scribblec test/popl14/Negotiation1.scr


Migration notes
---------------

Changes relative to upstream, made to port the tool to Python 3:

- src/scribble/**/*.py: mechanical 2to3 conversion (fissix) plus hand fixes for
  the things a mechanical port cannot resolve, notably:

  * implicit relative imports converted to absolute imports in the
    "scribble" package (the tool is now invoked as "python3 -m scribble.main",
    so src/ is on PYTHONPATH), and "from . import a.b" fixups;
  * locals named "next" that shadowed the builtin and then broke "next(...)"
    calls (renamed to next_);
  * iterator.next() replaced with next(iterator);
  * token.setText() replaced with the ANTLR 3.5 Python3 runtime's token.text
    setter in scrib_util.set_node_type();
  * role lists derived from sets are sorted so generated local protocols are
    byte-for-byte reproducible: Py3 hashes strings with a per-process seed, so
    unordered iteration produced randomly ordered "throws ... to" clauses.

- src/scribble/Scribble.g: the ANTLR target is now "Python3".

- antlr/: the vendored ANTLR 3.1.3 jar and its Python 2 runtime have been
  replaced by antlr-3.5.3-complete.jar and the upstream ANTLR 3.5 Python3
  runtime (from https://github.com/antlr/antlr3, runtime/Python3). The 3.1.3
  Python target emits Python 2 code and its runtime does not run on Python 3.

- run/scribblec, run/scribblec-build: updated for python3, the 3.5.3 jar and
  the "scribble" package layout.

Behavioural equivalence was checked against Python 2.7 (python:2.7-slim in a
container): for every global protocol in test/popl14 (40 protocol/role
projections), validation succeeds and the generated local protocols are
byte-identical to the Python 2 output.
