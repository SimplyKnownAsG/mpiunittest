
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
    print('Found {} suites, will distribute across {} processors.'
          .format(len(suites), mut.SIZE - 1))
    for suite in suites:
      actions.RequestWorkAction.add_work(RunSuiteAction(suite))
    waiting = [True] + [False for _ in range(1, mut.SIZE)]
    while actions.RequestWorkAction._backlog or not all(waiting):
      for rank in range(1, mut.SIZE):
        workRequest = mut.COMM_WORLD.recv(None, source=rank)
        if not isinstance(workRequest, actions.Action):
          raise actions.MpiActionError(workRequest)
        workRequest.invoke()
        waiting[rank] = isinstance(workRequest, actions.RequestWorkAction)
    for _ in range(1, mut.SIZE):
      mut.COMM_WORLD.send(actions.StopAction(), dest=_)
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
    # result._original_stdout.write('[{:0>3}] running\n'.format(mut.RANK))
    self._result = result
    not_done = True
    while not_done:
      # result._original_stdout.write('[{:0>3}] sending request\n'.format(mut.RANK))
      mut.COMM_WORLD.send(actions.RequestWorkAction())
      action = mut.COMM_WORLD.recv(None, source=0)
      # result._original_stdout.write('[{:0>3}] received {}\n'.format(mut.RANK, action))
      if not isinstance(action, actions.Action):
        raise actions.MpiActionError(action)
      not_done = action.invoke()
