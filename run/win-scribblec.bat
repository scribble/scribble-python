REM
REM  Has to be run from scribblec base directory. 
REM  Quickly hacked for use in Eclipse.
REM

set PYTHONPATH=%PYTHONPATH%;lib;parser

REM python src/scribble/main.py %~n1
python src/scribble/Main.py %*

