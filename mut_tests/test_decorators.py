
from __future__ import absolute_import, print_function

import sys
import unittest

import mut
from mut import __main__ as lion_mane
from mut import decorators
from mut_tests import suite_writers
from mut_tests import base_test

class SlowDecoratorTests(base_test.BaseTest):

    def test_slowDecorator(self):
        sw = suite_writers.SuiteWriter((mut.SIZE - 2) * 2, 20, 3.0)
        sw.write()
        sw = suite_writers.SuiteWriter(1, 1, 5.0)
        sw.add_decorator('@mut.slow_test(100)')
        sw.write()
        program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
        result = program.result
        self.check_results_for_failures(result)
        tests_run = mut.MPI_WORLD.allgather(result.testsRun)
        self.assertEqual(0, tests_run.pop(mut.DISPATCHER_RANK))
        self.assertIn(1, tests_run)
        tests_run.remove(1)
        self.assertTrue(all(40 == count for count in tests_run))

    def test_slowDecoratorCanBeAppliedToClass(self):
        @decorators.slow_test(100)
        class A(object):
            pass
        self.assertEqual(100, A.__mut_slow_estimate__)
        a = A()
        self.assertEqual(100, a.__mut_slow_estimate__)

    def test_slowDecoratorCannotBeAppliedToMethod(self):
        with self.assertRaises(decorators.DecoratorError):
            @decorators.slow_test(100)
            def some_method():
                pass

    def test_slowDecoratorDefaultsToMaxInt(self):
        @decorators.slow_test()
        class A(object):
            pass
        self.assertEqual(sys.maxint, A.__mut_slow_estimate__)
        a = A()
        self.assertEqual(sys.maxint, a.__mut_slow_estimate__)


class ParallelDecoratorTests(base_test.BaseTest):

    def test_parallelDecorator(self):
        sw = suite_writers.SuiteWriter(3, 7, 3.0)
        sw.add_decorator('@mut.parallel()')
        sw.write()
        program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
        result = program.result
        self.check_results_for_failures(result)
        tests_run = mut.MPI_WORLD.allgather(result.testsRun)
        self.assertEqual(21, tests_run.pop(mut.DISPATCHER_RANK))
        self.assertTrue(all(21 == count for count in tests_run))

    def test_parallelDecoratorCanBeAppliedToAClass(self):
        @decorators.parallel(4)
        class A(object):
            pass
        self.assertEqual(4, A.__mut_parallel__)
        a = A()
        self.assertEqual(4, a.__mut_parallel__)
 
    def test_parallelDecoratorDefaultsToAMinimumOf2Processors(self):
        @decorators.parallel()
        class A(object):
            pass
        self.assertEqual(2, A.__mut_parallel__)
        a = A()
        self.assertEqual(2, a.__mut_parallel__)
        
    def test_parallelDecoratorCannotBeAppliedToMethod(self):
        with self.assertRaises(decorators.DecoratorError):
            @decorators.parallel(100)
            def some_method():
                pass


if __name__ == '__main__':
    unittest.main()
