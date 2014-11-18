
from __future__ import absolute_import

import sys
from unittest import main as TestProgram
from unittest import loader
from unittest import runner

from . import actions
from . import suites
from . import results
from . import runners

class MpiTestProgram(TestProgram):

  def __init__(self, argv):
    loader.TestLoader.suiteClass = suites.MpiTestSuite
    TestProgram.__init__(self,
                         exit=False,
                         testRunner=runners.MpiTestRunner,
                         argv=argv)
