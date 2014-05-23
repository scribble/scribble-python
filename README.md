scribble-python
===============

scribblec is a command line tool for validating the well-formedness of Scribble global protocols and peforming the projection to local protocols.

Building and running the scribblec tool has been tested on Ubuntu Linux and Cygwin/Windows.


Building the tool
-----------------

- Requirements: Java RE 7 or later, Python 2.7.3 or higher

- From the scribble-python base directory:

  run/scribblec-build


Running the tool
----------------

We use the test/popl4/Neogitation1.scr Scribble source file as an example.

- To validate the well-formedness of all global protocols, from the scribble-python base directory:

  run/scribblec test/popl14/Negotiation1.scr

- To additionally project the "Negotiate" global protocol in this file to the local protocol for role "Consumer", to the output directory "output":

  run/scribblec test/popl14/Negotiation1.scr -project popl14.Negotiation1.Negotiate Consumer -o output

