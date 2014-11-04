
from __future__ import absolute_import

import sys
import cStringIO
from unittest import suite
from unittest import case
from unittest import runner

import mut
from . import actions


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
      self.tryClassSetUpOrTearDown(test, result, 'setUpClass')
      if result.shouldStop:
        break
      test(result)
      self.tryClassSetUpOrTearDown(test, result, 'tearDownClass')
    return not result.shouldStop

  def tryClassSetUpOrTearDown(self, test, result, methodName):
    method = getattr(test, methodName, None)
    if method is not None:
      sys.stdout = cStringIO.StringIO()
      sys.stderr = cStringIO.StringIO()
      try:
        method()
      except:
        if not hasattr(sys.stdout, 'getvalue'):
          sys.stdout = cStringIO.StringIO()
          sys.stdout.write('[mut.{:0>3}] sys.stdout has been modified'
                           .format(mut.RANK))
        if not hasattr(sys.stderr, 'getvalue'):
          sys.stderr = cStringIO.StringIO()
          sys.stderr.write('[mut.{:0>3}] sys.stderr has been modified'
                           .format(mut.RANK))
        result.addError(test, sys.exc_info())
      finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
    

class MasterTestSuite(SerialTestSuite):

  def run(self, result, debug=False):
    self._result = result
    suites = self._flatten()
    result.stream.writeln('Found {} suites, will distribute across {} processors.'
                          .format(len(suites), mut.SIZE - 1))
    for suite in suites:
      actions.RequestWorkAction.add_work(RunSuiteAction(suite))
    waiting = [True] + [False for _ in range(1, mut.SIZE)]
    while actions.RequestWorkAction._backlog or not all(waiting):
      for rank in range(1, mut.SIZE):
        if not mut.COMM_WORLD.Iprobe(source=rank):
          continue
        mpi_action = mut.COMM_WORLD.recv(source=rank)
        if not isinstance(mpi_action, actions.Action):
          raise actions.MpiActionError(mpi_action)
        mpi_action.invoke()
        waiting[rank] = isinstance(mpi_action, actions.RequestWorkAction)
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
    self._result = result
    not_done = True
    while not_done:
      mut.COMM_WORLD.send(actions.RequestWorkAction())
      action = mut.COMM_WORLD.recv(None, source=0)
      # result._original_stdout.write('[{:0>3}] received {}\n'.format(mut.RANK, action))
      if not isinstance(action, actions.Action):
        raise actions.MpiActionError(action)
      not_done = action.invoke()
