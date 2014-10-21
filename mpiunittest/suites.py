
from unittest import suite
from unittest import case
from unittest import runner

import mpiunittest as mut
from mpiunittest import actions

class SerialTestSuite(suite.TestSuite):
  pass

class MasterTestSuite(suite.TestSuite):

  def run(self, result, debug=False):
    suites = self._flatten()
    while len(suites) > 0:
      if result.shouldStop:
        break
      for rank in range(1, mut.SIZE):
        if len(suites) == 0:
          break
        mut.COMM_WORLD.send(suites.pop(0), dest=rank)
    quit = actions.StopAction()
    for rank in range(1, mut.SIZE):
      mut.COMM_WORLD.send(quit, dest=rank)
    return result
  
  def invoke(self, result):
    for test in self:
      if result.shouldStop:
        break
      test(result)
    return True

  def _flatten(self):
    suites = []
    for ss in self:
      if isinstance(ss, MasterTestSuite):
        suites.extend(ss._flatten())
    if len(self._tests) > 0 and all(isinstance(ss, case.TestCase) for ss in self):
      suites.append(self)
    return suites


class WorkerTestSuite(suite.TestSuite):

  def run(self, result, debug=False):
    not_done = True
    while not_done:
      action = mut.COMM_WORLD.recv(None, source=0)
      try:
        not_done = action.invoke()
      except:
        not_done = action.invoke(result)

