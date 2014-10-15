import sys
from unittest import main as TestProgram
from unittest import loader

from mpiunittest import actions
from mpiunittest import suites

class SerialTestProgram(TestProgram):
  pass


class MasterTestProgram(TestProgram):

  def __init__(self, **kwargs):
    loader.TestLoader.suiteClass = suites.MasterTestSuite
    kwargs['exit'] = False
    TestProgram.__init__(self, **kwargs)


class WorkerTestProgram(TestProgram):

  def __init__(self, **kwargs):
    loader.TestLoader.suiteClass = suites.WorkerTestSuite
    kwargs['exit'] = False
    TestProgram.__init__(self, **kwargs)

