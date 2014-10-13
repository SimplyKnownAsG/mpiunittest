
from unittest import suite
from unittest import case

import mpiunittest as mut
from mpiunittest import actions

class SerialTestSuite(suite.TestSuite):
  pass


class MasterTestSuite(suite.TestSuite):

  indent = ''
  def run(self, result, debug=False):
    for suite in self._flatten():
      if result.shouldStop:
        break
      for test in suite:
        if result.shouldStop:
          break
        test(result)
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


class WorkerTestSuite(suite.TestSuite):

  def run(self, result, debug=False):
    not_done = True
    while not_done:
      action = mut.COMM_WORLD.recv(None, source=0)
      not_done = action.invoke()

