import sys
from unittest import main as TestProgram
from unittest import loader
from unittest import runner

from mpiunittest import actions
from mpiunittest import suites
from mpiunittest import results
from mpiunittest import runners

class SerialTestProgram(TestProgram):
  pass


class MasterTestProgram(TestProgram):

  def __init__(self):
    loader.TestLoader.suiteClass = suites.MasterTestSuite
    TestProgram.__init__(self, exit=False, testRunner=runners.MasterTestRunner)

class WorkerTestProgram(TestProgram):

  def __init__(self):
    loader.TestLoader.suiteClass = suites.WorkerTestSuite
    TestProgram.__init__(self, exit=False, testRunner=runners.WorkerTestRunner)

