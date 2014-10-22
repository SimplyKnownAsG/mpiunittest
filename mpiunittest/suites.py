
from unittest import suite
from unittest import case
from unittest import runner

import mpiunittest as mut
from mpiunittest import actions


class SerialTestSuite(suite.TestSuite):
  _instance = None
  
  def __init__(self, *args, **kwargs):
    suite.TestSuite.__init__(self, *args, **kwargs)
    SerialTestSuite._instance = self
    self._result = None
  
  @classmethod
  def get_instance(cls):
    return cls._instance


class RunSuiteAction(actions.Action):
  
  def __init__(self, suite):
    self._suite = suite
  
  def invoke(self):
    result = SerialTestSuite.get_instance()._result
    for test in self._suite:
      if result.shouldStop:
        break
      test(result)
    return not result.shouldStop


class MasterTestSuite(SerialTestSuite):

  def run(self, result, debug=False):
    self._result = result
    suites = self._flatten()
    while len(suites) > 0:
      if result.shouldStop:
        break
      for rank in range(1, mut.SIZE):
        if len(suites) == 0:
          break
        suiteAction = RunSuiteAction(suites.pop(0))
        mut.COMM_WORLD.send(suiteAction, dest=rank)
      # mut.COMM_WORLD.irecv()
    quit = actions.StopAction()
    for rank in range(1, mut.SIZE):
      mut.COMM_WORLD.send(quit, dest=rank)
    return result
  
  def _flatten(self):
    suites = []
    for ss in self:
      if isinstance(ss, MasterTestSuite):
        suites.extend(ss._flatten())
    if len(self._tests) > 0 and all(isinstance(ss, case.TestCase) for ss in self):
      suites.append(self)
    return suites


class WorkerTestSuite(SerialTestSuite):

  def run(self, result, debug=False):
    self._result = result
    not_done = True
    while not_done:
      action = mut.COMM_WORLD.recv(None, source=0)
      if not isinstance(action, actions.Action):
        raise actions.MpiActionError(action)
      not_done = action.invoke()

