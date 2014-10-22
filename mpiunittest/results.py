from __future__ import absolute_import

from unittest import runner
from unittest import result

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


class SerialTestResultHandler(runner.TextTestResult):
  
  _instance = None
  
  def __init__(self, *args, **kwargs):
    runner.TextTestResult.__init__(self, *args, **kwargs)
    SerialTestResultHandler._instance = self
  
  @classmethod
  def get_instance(cls):
    return cls._instance


class MasterTestResultHandler(SerialTestResultHandler):
  pass


class WorkerTestResultHandler(SerialTestResultHandler):

  def __init__(self, stream, descriptions, verbosity):
    SerialTestResultHandler.__init__(self, stream, descriptions, verbosity)
    self.stream = stream
    self.showAll = verbosity > 1
    self.dots = verbosity == 1
    self.descriptions = descriptions

  def addSuccess(self, test):
    action = ResultAction(test, 'addSuccess', None, None)
    mpiunittest.COMM_WORLD.send(action, dest=0)

  def addError(self, test, err):
    action = ResultAction(test, 'addError', err, None)
    mpiunittest.COMM_WORLD.send(action, dest=0)

  def addFailure(self, test, err):
    action = ResultAction(test, 'addFailure', err, None)
    mpiunittest.COMM_WORLD.send(action, dest=0)

  def addSkip(self, test, reason):
    action = ResultAction(test, 'addSkip', None, reason)
    mpiunittest.COMM_WORLD.send(action, dest=0)

  def addExpectedFailure(self, test, err):
    action = ResultAction(test, 'addExpectedFailure', err, None)
    mpiunittest.COMM_WORLD.send(action, dest=0)

  def addUnexpectedSuccess(self, test):
    action = ResultAction(test, 'addUnexpectedSuccess', None, None)
    mpiunittest.COMM_WORLD.send(action, dest=0)

  def printErrors(self):
    pass

  def printErrorList(self, flavour, errors):
    pass
