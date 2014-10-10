import sys

from unittest.main import TestProgram

class SerialTestProgram(TestProgram):

  def parseArgs(self, argv):
    # allow multiple definitions, and prevent work from occuring immediately
    pass

  def runTests(self):
    # prevent __init__ from starting work... this is more complicated.
    pass

  def parse_args(self):
    TestProgram.parseArgs(self, sys.argv)

  def run_tests(self):
    TestProgram.runTests(self)


class MasterTestProgram(SerialTestProgram):

  def run_tests(self):
    pass
    # TestProgram.runTests(self)

class WorkerTestProgram(SerialTestProgram):

  def run_tests(self):
    pass
    # TestProgram.runTests(self)

