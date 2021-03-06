
from __future__ import absolute_import

import sys
from unittest import runner
import cStringIO
import timeit

import mut
from . import results


class MpiTestRunner(runner.TextTestRunner):

  def __init__(self,
               stream=None,
               descriptions=True,
               verbosity=1,
               failfast=False,
               buffer=False,
               resultclass=None):
    if mut.RANK == 0:
      resultclass = resultclass or results.MasterTestResultHandler
      stream = stream or sys.stderr
    else:
      resultclass = resultclass or results.WorkerTestResultHandler
      stream = stream or cStringIO.StringIO()
    resultClass = results.MasterTestResultHandler if mut.RANK == 0 else results.WorkerTestResultHandler
    runner.TextTestRunner.__init__(self,
                                   stream=stream,
                                   descriptions=descriptions,
                                   verbosity=verbosity,
                                   failfast=failfast,
                                   buffer=buffer,
                                   resultclass=resultclass)

  def run(self, test):
    "Run the given test case or test suite."
    result = self._setUpResultClass()
    timeTaken = self._runTests(test, result)
    result.summarizeResults(timeTaken)
    return result

  def _setUpResultClass(self):
    result = self._makeResult()
    runner.registerResult(result)
    result.failfast = self.failfast
    result.buffer = self.buffer
    return result

  def _runTests(self, test, result):
    startTime = timeit.default_timer()
    startTestRun = getattr(result, 'startTestRun', None)
    if startTestRun is not None:
      startTestRun()
    try:
      test(result)
    finally:
      stopTestRun = getattr(result, 'stopTestRun', None)
      if stopTestRun is not None:
        stopTestRun()
    stopTime = timeit.default_timer()
    return stopTime - startTime
 