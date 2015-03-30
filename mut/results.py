
from __future__ import absolute_import

import time
from unittest import runner
from unittest import result
import six

import mut
from mut import actions
from mut import logger


class MpiTestResultHandler(runner.TextTestResult):
  
    _instance = None
  
    def __init__(self, *args, **kwargs):
        runner.TextTestResult.__init__(self, *args, **kwargs)
        MpiTestResultHandler._instance = self
    
    @classmethod
    def get_instance(cls):
        return cls._instance
    
    def summarizeResults(self, timeTaken):
        self.printErrors()
        self._printTestsPerSecond(timeTaken)
        self._printInfos_HASHTAG_BadName()
     
    def printErrors(self):
        message = ''
        if mut.RANK != mut.DISPATCHER_RANK:
            runner.TextTestResult.printErrors(self)
            message = self.stream.getvalue()
        logger.all_log(message)
      
    def _printTestsPerSecond(self, timeTaken):
        if hasattr(self, 'separator2'):
            self.stream.writeln(self.separator2)
        ran = self.testsRun
        total_tests = mut.MPI_WORLD.allgather(self.testsRun)
        msg_prefix = 'Ran '
        if mut.RANK == mut.DISPATCHER_RANK:
            logger.write('\n')
            ran = sum(total_tests) - total_tests[mut.DISPATCHER_RANK] * (mut.SIZE - 1)
            msg_prefix = 'Dispatched a total of '
        msg = '{} test{} in {:.4f}s'.format(ran, (ran != 1) * 's', timeTaken)
        if total_tests[mut.DISPATCHER_RANK] > 1:
            msg += ', {} tests were parallel.'.format(total_tests[0])
        elif total_tests[mut.DISPATCHER_RANK] > 0:
            msg += ', 1 test was parallel.'
        else:
            msg += '.'
        logger.all_log(msg_prefix + msg)

    def _printInfos_HASHTAG_BadName(self):
        details = [('failures', mut.mpi_length(self.failures)),
                   ('errors', mut.mpi_length(self.errors)),
                   ('skipped', mut.mpi_length(self.skipped)),
                   ('expected failures', mut.mpi_length(self.expectedFailures)),
                   ('unexpected successes', mut.mpi_length(self.unexpectedSuccesses))
                  ]
        short_result = 'OK' if details[0][1] < 1 and details[1][1] < 1 else 'FAILED'
        msg = ('{} ({})'
               .format(short_result,
                       ', '.join('{}={}'.format(nn, cc) for nn, cc in details)))
        if mut.RANK == mut.DISPATCHER_RANK:
            msg = 'summary: ' + msg
        logger.all_log(msg)

    def _flush_stream(self):
        message = self.stream.getvalue()
        logger.write(message)
        del(self.stream)
        self.stream = runner._WritelnDecorator(six.StringIO())
  
    def addSuccess(self, test):
        runner.TextTestResult.addSuccess(self, test)
        self._flush_stream()

    def addError(self, test, err):
        runner.TextTestResult.addError(self, test, err)
        self._flush_stream()

    def addFailure(self, test, err):
        runner.TextTestResult.addFailure(self, test, err)
        self._flush_stream()

    def addSkip(self, test, reason):
        runner.TextTestResult.addSkip(self, test, reason)
        self._flush_stream()

    def addExpectedFailure(self, test, err):
        runner.TextTestResult.addSkip(self, test, err)
        self._flush_stream()

    def addUnexpectedSuccess(self, test):
        runner.TextTestResult.addUnexpectedSuccess(self, test)
        self._flush_stream()

