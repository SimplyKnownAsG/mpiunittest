
from __future__ import absolute_import

import sys
import traceback
import cStringIO
from unittest import suite
from unittest import case
from unittest import runner

import mut
from . import actions


class MpiTestSuite(suite.TestSuite):
  _instance = None
  
  def __init__(self, *args, **kwargs):
    suite.TestSuite.__init__(self, *args, **kwargs)
    MpiTestSuite._instance = self
    self._result = None
    self._flattened_suites = _SuiteCollection()
    self._debug = False
  
  @classmethod
  def get_instance(cls):
    return cls._instance

  def run(self, result, debug=False):
    self._debug = debug
    self._result = result
    suites = self._flatten()
    self._confirm_process_loaded_same_tests()
    if mut.RANK == 0:
      self._run_as_master()
    else:
      self._run_as_worker()

  def _flatten(self):
    for ss in self:
      if isinstance(ss, MpiTestSuite):
        self._flattened_suites.update(ss._flatten())
    if len(self._tests) > 0 and all(isinstance(ss, case.TestCase) for ss in self):
      self._flattened_suites.add(self)
    return self._flattened_suites

  def _confirm_process_loaded_same_tests(self):
    loaded_suite_names = mut.COMM_WORLD.gather(self._flattened_suites.keys(), root=0)
    if mut.RANK == 0:
      master_suite_names = loaded_suite_names[0]
      if self._debug:
        sys.__stderr__.write('[{:0>3}] Checking that all processors loaded same tests.\n'.format(mut.RANK))
      for worker_suite_names in loaded_suite_names[1:]:
        if master_suite_names != worker_suite_names:
          if self._debug:
            sys.__stderr__.write('[{:0>3}] shit failed, \n{} vs.\n{}.\n'.format(mut.RANK, master_suite_names, worker_suite_names))
          raise Exception('Worker and master did not load the same tests... this is an issue.')

  def _run_as_master(self):
    self._result.stream.writeln('Found {} suites, will distribute across {} processors.'
                                .format(len(self._flattened_suites), mut.SIZE - 1))
    for suite_name in self._flattened_suites.keys():
      actions.RequestWorkAction.add_work(RunSuiteAction(suite_name))
    waiting = [True] + [False for _ in range(1, mut.SIZE)]
    while actions.RequestWorkAction._backlog or not all(waiting):
      for rank in range(1, mut.SIZE):
        if not mut.COMM_WORLD.Iprobe(source=rank):
          continue
        mpi_action = mut.COMM_WORLD.recv(source=rank)
        if not isinstance(mpi_action, actions.Action):
          raise actions.MpiActionError(mpi_action)
        mpi_action.invoke()
        if self._debug:
          sys.__stderr__.write('[{:0<3}] backlog: {}, waiting: {}\n'.format(mut.RANK, len(actions.RequestWorkAction._backlog), all(waiting)))
        waiting[rank] = isinstance(mpi_action, actions.RequestWorkAction)
    for rank in range(1, mut.SIZE):
      mut.COMM_WORLD.send(actions.StopAction(), dest=rank)
      if self._debug:
        sys.__stderr__.write('[{:0<3}] telling {} to stop.\n'.format(mut.RANK, rank))
    return self._result
  
  def _run_as_worker(self):
    not_done = True
    try:
      while not_done:
        if self._debug:
          sys.__stderr__.write('[{:0>3}] waiting...\n'.format(mut.RANK))
        mut.COMM_WORLD.send(actions.RequestWorkAction())
        action = mut.COMM_WORLD.recv(None, source=0)
        if self._debug:
          sys.__stderr__.write('[{:0>3}] sent {}\n'.format(mut.RANK, action))
        if not isinstance(action, actions.Action):
          raise actions.MpiActionError(action)
        if self._debug:
          sys.__stderr__.write('[{:0>3}] {}.\n'.format(mut.RANK, action))
        not_done = action.invoke()
    except:
      traceback.print_exc(file=sys.__stderr__)
      if self._debug:
        sys.__stderr__.write('[{:0>3}] worker node failed, quitting.\n'.format(mut.RANK))
      mut.COMM_WORLD.Abort(-1)


class _SuiteCollection(dict):
  
  def __setitem__(self, key, value):
    if key in self:
      raise KeyError('Item with key {} already exists'.format(key))
    dict.__setitem__(self, key, value)
  
  def add(self, suite):
    tests = iter(suite)
    first_test = tests.next()
    fully_qualified_class = '{}.{}'.format(first_test.__module__, first_test.__class__.__name__)
    for test in tests:
      if test.__class__ != first_test.__class__:
        raise Exception('A flattened suite should only contain instances of the same type, but '
                        'found {} and {}'.format(first_test, test))
    self[fully_qualified_class] = suite

  def ordered(self):
    pass


class RunSuiteAction(actions.Action):
  
  def __init__(self, suite_name):
    self._suite_name = suite_name
  
  def invoke(self):
    local_suite = MpiTestSuite.get_instance()
    result = local_suite._result
    for test in local_suite._flattened_suites[self._suite_name]:
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
