====
Contributing
====

Go for it, but please read below!

Python Version
==============

Currently using Python 2.7 with lots of imports from __future___.

Project Structure
=================

The project structure is this:

  ./mpiunittest/ -- source files, the "actual" package
  ./sample_tests/ -- sample tests.

Running tests
=============

From the command line:

  $ mpiexec -n 5 python -m mpiunittest discover -s sample_tests/

The command line options from `unittest` are also supported, such as `-b` and
`-v`. 
