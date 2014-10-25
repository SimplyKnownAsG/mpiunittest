from __future__ import absolute_import

import time
from unittest import runner
from unittest import result
import cStringIO

import mpiunittest
from . import actions


class ResultAction(actions.Action):
  
  def __init__(self, test, method_name, err, reason):
    self._test = test
    self._method = method_name
    self._err = err
    self._reason = reason
  
  def invoke(self):
    handler = SerialTestResultHandler.get_instance()
    method = getattr(handler, self._method)
    args = [aa for aa in (self._method, self._err, self._reason)
            if aa is not None]
    #print('[{:0>3}] result_action: {}'.format(mpiunittest.RANK, self._method))
    method(*args)
    return True


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
