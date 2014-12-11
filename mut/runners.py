
from __future__ import absolute_import

import sys
from unittest import runner
import six
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
        resultclass = resultclass or results.MpiTestResultHandler
        stream = stream or six.StringIO()
        runner.TextTestRunner.__init__(self,
                                       stream=stream,
                                       descriptions=descriptions,
                                       verbosity=verbosity,
                                       failfast=failfast,
                                       buffer=buffer,
                                       resultclass=resultclass)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._set_up_results_class()
        timeTaken = self._runTests(test, result)
        result.summarizeResults(timeTaken)
        return result

    def _set_up_results_class(self):
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
