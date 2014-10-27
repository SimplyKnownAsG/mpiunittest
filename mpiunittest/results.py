from __future__ import absolute_import

import time
from unittest import runner
from unittest import result
import cStringIO

import mpiunittest
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
    if hasattr(self, 'separator2'):
      self.stream.writeln(self.separator2)
    run = self.testsRun
    self.stream.writeln("Ran %d test%s in %.4fs" %
                        (run, run != 1 and "s" or "", timeTaken))
    self.stream.writeln()

    expectedFails = unexpectedSuccesses = skipped = 0
    try:
      expectedFailures = len(self.expectedFailures)
      unexpectedSuccesses = len(self.unexpectedSuccesses)
      skipped = len(self.skipped)
    except AttributeError:
      pass

    infos = []
    if not self.wasSuccessful():
      self.stream.write("FAILED")
      failed, errored = map(len, (self.failures, self.errors))
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
    mpiunittest.COMM_WORLD.send(action, dest=0)
  
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

  def printErrors(self):
    pass

  def printErrorList(self, flavour, errors):
    pass
