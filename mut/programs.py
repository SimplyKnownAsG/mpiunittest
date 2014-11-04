from __future__ import absolute_import

from __future__ import absolute_import

import sys
from unittest import main as TestProgram
from unittest import loader
from unittest import runner

from . import actions
from . import suites
from . import results
from . import runners

class SerialTestProgram(TestProgram):
  pass


class MasterTestProgram(TestProgram):

  def __init__(self):
    loader.TestLoader.suiteClass = suites.MasterTestSuite
    TestProgram.__init__(self, exit=False, testRunner=runners.MpiTestRunner)

class WorkerTestProgram(TestProgram):

  def __init__(self):
    loader.TestLoader.suiteClass = suites.WorkerTestSuite
    TestProgram.__init__(self, exit=False, testRunner=runners.MpiTestRunner)
