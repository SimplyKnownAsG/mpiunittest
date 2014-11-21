
from __future__ import absolute_import

import time
from unittest import runner
from unittest import result
import six

import mut
from . import actions


class SimpleResultAction(actions.Action):
  
  def __init__(self, message):
    self._message = message
  
  def invoke(self):
    handler = SerialTestResultHandler.get_instance()
    handler.printResult(self._message)
    return True


class SerialTestResultHandler(runner.TextTestResult):
  
  _instance = None
  
  def __init__(self, *args, **kwargs):
    runner.TextTestResult.__init__(self, *args, **kwargs)
    SerialTestResultHandler._instance = self
  
  @classmethod
  def get_instance(cls):
    return cls._instance

  def summarizeResults(self, timeTaken):
    self.printErrors()
    self._printTestsPerSecond(timeTaken)
    self._printInfos_HASHTAG_BadName()
  
  def flush(self):
    self.stream.write('\n')
    self.stream.flush()
    
  def printErrors(self):
    message = ''
    self.flush()
    if mut.RANK != 0:
      runner.TextTestResult.printErrors(self)
      message = self.stream.getvalue()
    mut.mpi_log(self.stream, message)
    
  def _printTestsPerSecond(self, timeTaken):
    if hasattr(self, 'separator2'):
      self.stream.writeln(self.separator2)
    ran = self.testsRun
    total_tests = mut.COMM_WORLD.gather(self.testsRun, root=0)
    msg_prefix = 'Ran '
    if mut.RANK == 0:
      ran = sum(total_tests)
      msg_prefix = 'Dispatched a total of '
    msg = '{} test{} in {:.4f}s'.format(ran, (ran != 1) * 's', timeTaken)
    mut.mpi_log(self.stream, msg_prefix + msg)

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
    if mut.RANK == 0:
      msg = 'summary: ' + msg
    mut.mpi_log(self.stream, msg)


class MasterTestResultHandler(SerialTestResultHandler):

  def printResult(self, message):
    self.stream.write(message)


class WorkerTestResultHandler(SerialTestResultHandler):

  def __init__(self, stream, descriptions, verbosity):
    SerialTestResultHandler.__init__(self, stream, descriptions, verbosity)

  def _flushStream(self):
    message = self.stream.getvalue()
    action = SimpleResultAction(message)
    mut.COMM_WORLD.send(action, dest=0)
    self.flush()
  
  def flush(self):
    del(self.stream)
    self.stream = runner._WritelnDecorator(six.StringIO())
  
  def addSuccess(self, test):
    SerialTestResultHandler.addSuccess(self, test)
    self._flushStream()

  def addError(self, test, err):
    SerialTestResultHandler.addError(self, test, err)
    self._flushStream()

  def addFailure(self, test, err):
    SerialTestResultHandler.addFailure(self, test, err)
    self._flushStream()

  def addSkip(self, test, reason):
    SerialTestResultHandler.addSkip(self, test, reason)
    self._flushStream()

  def addExpectedFailure(self, test, err):
    SerialTestResultHandler.addSkip(self, test, reason)
    self._flushStream()

  def addUnexpectedSuccess(self, test):
    SerialTestResultHandler.addUnexpectedSuccess(self, test)
    self._flushStream()
