
from __future__ import absolute_import

import sys
from unittest import runner
import cStringIO
import timeit

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

  def run(self, test):
    "Run the given test case or test suite."
    result = self._setUpResultClass()
    timeTaken = self._runTests(test, result)
    self._summarizeResults(result, timeTaken)
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
 
  def _summarizeResults(self, result, timeTaken):
    result.printErrors()
    if hasattr(result, 'separator2'):
      self.stream.writeln(result.separator2)
    run = result.testsRun
    self.stream.writeln("Ran %d test%s in %.4fs" %
                        (run, run != 1 and "s" or "", timeTaken))
    self.stream.writeln()

    expectedFails = unexpectedSuccesses = skipped = 0
    try:
      expectedFailures = len(result.expectedFailures)
      unexpectedSuccesses = len(result.unexpectedSuccesses)
      skipped = len(result.skipped)
    except AttributeError:
      pass

    infos = []
    if not result.wasSuccessful():
      self.stream.write("FAILED")
      failed, errored = map(len, (result.failures, result.errors))
      if failed:
        infos.append("failures=%d" % failed)
      if errored:
        infos.append("errors=%d" % errored)
    else:
      self.stream.write("OK")
    if skipped:
      infos.append("skipped=%d" % skipped)
    if expectedFails:
      infos.append("expected failures=%d" % expectedFails)
    if unexpectedSuccesses:
      infos.append("unexpected successes=%d" % unexpectedSuccesses)
    if infos:
      self.stream.writeln(" (%s)" % (", ".join(infos),))
    else:
      self.stream.write("\n")


class WorkerTestRunner(runner.TextTestRunner):

  def __init__(self,
               stream=sys.stderr,
               descriptions=True,
               verbosity=1,
               failfast=False,
               buffer=False,
               resultclass=None):
    runner.TextTestRunner.__init__(self,
                                   stream=cStringIO.StringIO(),
                                   descriptions=descriptions,
                                   verbosity=verbosity,
                                   failfast=failfast,
                                   buffer=buffer,
                                   resultclass=results.WorkerTestResultHandler)
