from __future__ import absolute_import

import time
from unittest import runner
from unittest import result
import cStringIO

import mpiunittest as mut
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
    
  def printErrors(self):
    self.errors = mut.mpi_flatten_gather(self.errors)
    self.failures = mut.mpi_flatten_gather(self.failures)
    if mut.RANK == 0:
      runner.TextTestResult.printErrors(self)
    
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
    details = [('failures', len(self.failures)),
               ('errors', len(self.errors)),
               ('skipped', mut.mpi_length(self.skipped)),
               ('expected failures', mut.mpi_length(self.expectedFailures)),
               ('unexpected successes', mut.mpi_length(self.unexpectedSuccesses))
              ]
    msg = ('{} ({})'
           .format('OK' if self.wasSuccessful() else 'FAILED',
                   ', '.join('{}={}'.format(nn, cc) for nn, cc in details)))
    mut.mpi_log(self.stream, msg)


class MasterTestResultHandler(SerialTestResultHandler):

  def printResult(self, message):
    self.stream.write(message)


class WorkerTestResultHandler(SerialTestResultHandler):

  def __init__(self, stream, descriptions, verbosity):
    SerialTestResultHandler.__init__(self, stream, descriptions, verbosity) 
  def _flushStream(self):
    message = self.stream.getvalue()
    del(self.stream)
    self.stream = runner._WritelnDecorator(cStringIO.StringIO())
    action = SimpleResultAction(message)
    mut.COMM_WORLD.send(action, dest=0)
  
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
