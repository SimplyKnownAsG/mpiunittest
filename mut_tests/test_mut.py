
from __future__ import absolute_import, print_function

import sys

import mut
from mut import __main__ as lion_mane
from mut_tests import suite_writers
from mut_tests import base_test


class MpiUnitTestTests(base_test.BaseTest):
 
    def test_equalDistribution(self):
        sw = suite_writers.SuiteWriter(mut.SIZE - 1, 10, 3.0)
        sw.write()
        program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
        result = program.result
        self.check_results_for_failures(result)
        self.assertEqual(result.testsRun, 10 if mut.RANK > mut.DISPATCHER_RANK else 0)

    def test_equalDistribution2(self):
        sw = suite_writers.SuiteWriter((mut.SIZE - 1) * 3, 5, 3.0)
        sw.write()
        program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
        result = program.result
        self.check_results_for_failures(result)
        self.assertEqual(result.testsRun, 15 if mut.RANK != mut.DISPATCHER_RANK else 0)

    def test_unequalDistribution(self):
        sw = suite_writers.SuiteWriter(mut.SIZE - 2, 20, 5.0)
        sw.write()
        sw = suite_writers.SuiteWriter(1, 1, 5.0)
        sw.write()
        program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
        result = program.result
        self.check_results_for_failures(result)
        tests_run = mut.MPI_WORLD.allgather(result.testsRun)
        self.assertEqual(0, tests_run.pop(mut.DISPATCHER_RANK))
        self.assertIn(1, tests_run)
        tests_run.remove(1)
        self.assertTrue(all(20 == count for count in tests_run))
    
    def test_pathIsTheSame(self):
        path = mut.MPI_WORLD.allgather(sys.path)
        for ii in range(1, len(path)):
            self.assertEqual(path[ii - 1], path[ii])

