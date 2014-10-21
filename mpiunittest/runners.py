
from __future__ import absolute_import

import sys
from unittest import runner
import cStringIO

from . import results

class MasterTestRunner(runner.TextTestRunner):

  def __init__(self,
               stream=sys.stderr,
               descriptions=True,
               verbosity=1,
               failfast=False,
               buffer=False,
               resultclass=None):
    runner.TextTestRunner.__init__(self,
                                   stream=sys.stderr,
                                   descriptions=descriptions,
                                   verbosity=verbosity,
                                   failfast=failfast,
                                   buffer=buffer,
                                   resultclass=results.MasterTestResultHandler)


class WorkerTestRunner(runner.TextTestRunner):

  def __init__(self,
               stream=sys.stderr,
               descriptions=True,
               verbosity=1,
               failfast=False,
               buffer=False,
               resultclass=None):
    runner.TextTestRunner.__init__(self,
                                   stream=sys.stderr,
                                   descriptions=descriptions,
                                   verbosity=verbosity,
                                   failfast=failfast,
                                   buffer=buffer,
                                   resultclass=results.WorkerTestResultHandler)
