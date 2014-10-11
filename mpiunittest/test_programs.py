import sys
from unittest.main import TestProgram

import mpiunittest as mut
from mpiunittest import actions

class SerialTestProgram(TestProgram):
  pass

class MasterTestProgram(TestProgram):

  def __init__(self, **kwargs):
    kwargs['exit'] = False
    TestProgram.__init__(self, **kwargs)

  def runTests(self):
    TestProgram.runTests(self)
    quit = actions.StopAction()
    for rank in range(1, mut.SIZE):
      mut.COMM_WORLD.send(quit, dest=rank)


class WorkerTestProgram(TestProgram):

  def runTests(self):
    not_done = True
    while not_done:
      action = mut.COMM_WORLD.recv(None, source=0)
      not_done = action.invoke()

