
from __future__ import absolute_import

import sys
import six
from unittest import suite
from unittest import case

import mut
from . import actions
from . import logger

class _SuiteCollection(dict):

    @property
    def parallel_suites(self):
        return [full_name for full_name, ss in self.items() if ss.is_parallel]

    @property
    def sorted_suites(self):
        candidates = {name: ss for name, ss in self.items() if not ss.is_parallel}
        sort_func = lambda (_, ss): -1 * getattr(ss, '__mut_slow_estimate__', float('inf'))
        sorted_values = sorted(candidates.items(), key=sort_func)
        return [full_name for full_name, _ in sorted_values]

    def add(self, suite):
        tests = iter(suite)
        first_test = tests.next()
        fully_qualified_class = '{}.{}'.format(first_test.__module__, first_test.__class__.__name__)
        for test in tests:
            if test.__class__ != first_test.__class__:
                raise Exception('A flattened suite should only contain instances of the same type, '
                                'but found {} and {}'.format(first_test, test))
        self[fully_qualified_class] = suite



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

    @property
    def is_parallel(self):
        tests = list(iter(self))
        return getattr(tests[0], '__mut_parallel__', -1) > 0

    def run(self, result, debug=False):
        self._debug = debug
        self._result = result
        self._flatten()
        self._confirm_process_loaded_same_tests()
        psuites = self._flattened_suites.parallel_suites
        if mut.RANK == mut.DISPATCHER_RANK:
            logger.log('Found {} suites, will distribute across {} processors.'
                       .format(len(self._flattened_suites), mut.SIZE - 1))
            if any(psuites):
                logger.log('Running {} suites in parallel'.format(len(psuites)))
        if mut.RANK == mut.DISPATCHER_RANK:
            self._run_as_dispatcher()
        else:
            self._run_as_worker()
        return result

    def _flatten(self):
        for ss in self:
            if isinstance(ss, MpiTestSuite):
                self._flattened_suites.update(ss._flatten())
        if len(self._tests) > 0 and all(isinstance(ss, case.TestCase) for ss in self):
            self._flattened_suites.add(self)
        return self._flattened_suites

    def _confirm_process_loaded_same_tests(self):
        loaded_suite_names = mut.DISPATCHER_COMM.gather(self._flattened_suites.keys(), root=0)
        if mut.RANK == 0:
            master_suite_names = loaded_suite_names[0]
            if self._debug:
                logger.log('Checking that all processors loaded same tests.\n')
            for worker_suite_names in loaded_suite_names[1:]:
                if master_suite_names != worker_suite_names:
                    if self._debug:
                        logger.log('something failed, \n{} vs.\n{}.\n'
                                   .format(master_suite_names, worker_suite_names))
                    raise Exception('Worker and dispatcher did not load the same tests... this is an issue.')

    def _run_as_dispatcher(self):
        worker_ranks = [rank for rank in range(mut.SIZE) if rank != mut.DISPATCHER_RANK]
        for suite_name in self._flattened_suites.parallel_suites:
            parallel_suite = RunSuiteAction(suite_name)
            for _ in worker_ranks:
                actions.RequestWorkAction.add_work(parallel_suite)
            self._result.testsRun += len(list(self._flattened_suites[suite_name]))
        self._dispatcher_loop()
        for suite_name in self._flattened_suites.sorted_suites:
            actions.RequestWorkAction.add_work(RunSuiteAction(suite_name))
        self._dispatcher_loop()
        for rank in worker_ranks:
            mut.DISPATCHER_COMM.send(actions.StopAction(), dest=rank)
            if self._debug:
                logger.log('telling {} to stop.\n'.format(rank))

    def _dispatcher_loop(self):
        worker_ranks = [rank for rank in range(mut.SIZE) if rank != mut.DISPATCHER_RANK]
        waiting_workers = {rank:False for rank in worker_ranks}
        while actions.RequestWorkAction._backlog or not all(waiting_workers.values()):
            for rank in worker_ranks:
                if not mut.DISPATCHER_COMM.Iprobe(source=rank):
                    continue
                mpi_action = mut.DISPATCHER_COMM.recv(source=rank)
                if not isinstance(mpi_action, actions.Action):
                    raise actions.MpiActionError(mpi_action)
                mpi_action.invoke()
                waiting_workers[rank] = isinstance(mpi_action, actions.RequestWorkAction)
            if self._debug:
                logger.log('backlog: {}, workers are waiting_workers: {}\n'
                           .format(len(actions.RequestWorkAction._backlog), all(waiting_workers.values())))

    def _run_as_worker(self):
        not_done = True
        logger.log('running as worker')
        while not_done:
            if self._debug:
                logger.log('waiting...')
            mut.DISPATCHER_COMM.send(actions.RequestWorkAction(), dest=mut.DISPATCHER_RANK)
            action = mut.DISPATCHER_COMM.recv(None, source=mut.DISPATCHER_RANK)
            if self._debug:
                logger.log('received {}\n'.format(action))
            if not isinstance(action, actions.Action):
                raise actions.MpiActionError(action)
            if self._debug:
                logger.log('{}.\n'.format(action))
            not_done = action.invoke()


class RunSuiteAction(actions.Action):
  
    def __init__(self, suite_name):
        self._suite_name = suite_name
    
    def invoke(self):
        local_suite = MpiTestSuite.get_instance()
        result = local_suite._result
        for test in local_suite._flattened_suites[self._suite_name]:
            self.try_class_set_up_or_tear_down(test, result, 'setUpClass')
            if result.shouldStop:
                break
            test(result)
            self.try_class_set_up_or_tear_down(test, result, 'tearDownClass')
        return not result.shouldStop
    
    def try_class_set_up_or_tear_down(self, test, result, methodName):
        method = getattr(test, methodName, None)
        if method is not None:
            sys.stdout = six.StringIO()
            sys.stderr = six.StringIO()
            try:
                method()
            except:
                if not hasattr(sys.stdout, 'getvalue'):
                    sys.stdout = six.StringIO()
                    sys.stdout.write('[mut.{:0>3}] sys.stdout has been modified'
                                     .format(mut.RANK))
                if not hasattr(sys.stderr, 'getvalue'):
                    sys.stderr = six.StringIO()
                    sys.stderr.write('[mut.{:0>3}] sys.stderr has been modified'
                                     .format(mut.RANK))
                result.addError(test, sys.exc_info())
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

