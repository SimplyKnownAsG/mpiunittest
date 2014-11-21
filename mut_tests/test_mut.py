
from __future__ import absolute_import, print_function

import unittest
import os
import glob

import mut
from mut import __main__ as lion_mane
from mut import programs
from . import suite_writers

class MpiUnitTestTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if mut.SIZE < 3:
      raise Exception('the unittests must be run with a RANK >= 4\n'
                      'try rerunning tests with something like:\n'
                      ' $ mpiexec -n 4 python -m unittest discover')

  @classmethod
  def tearDownClass(cls):
    if mut.RANK == 0:
      for test_file in glob.glob(suite_writers.SuiteWriter.file_prefix + '*'):
        os.remove(test_file)

  def setUp(self):
    self.tearDownClass()

  def tearDown(self):
    self.tearDownClass()
    
  def _check_results_for_failures(self, result):
    self.assertEqual(len(result.expectedFailures), 0)
    self.assertEqual(len(result.failures), 0)
    self.assertEqual(len(result.skipped), 0)
    self.assertEqual(len(result.errors), 0)
    self.assertEqual(len(result.unexpectedSuccesses), 0)
    self.assertEqual(result.wasSuccessful(), True)
  
  def test_equalDistribution(self):
    sw = suite_writers.SuiteWriter(mut.SIZE - 1, 10, 1.0)
    sw.write()
    program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
    result = program.result
    self._check_results_for_failures(result)
    self.assertEqual(result.testsRun, 10 if mut.RANK > 0 else 0)

  def test_equalDistribution2(self):
    sw = suite_writers.SuiteWriter((mut.SIZE - 1) * 3, 5, 1.0)
    sw.write()
    program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
    result = program.result
    self._check_results_for_failures(result)
    self.assertEqual(result.testsRun, 15 if mut.RANK > 0 else 0)

  def test_unequalDistribution(self):
    sw = suite_writers.SuiteWriter(mut.SIZE - 2, 20, 5.0)
    sw.write()
    sw = suite_writers.SuiteWriter(1, 1, 5.0)
    sw.write()
    program = lion_mane.get_test_program(['mut', 'discover', '-p', 'sample_*.py'])
    result = program.result
    self._check_results_for_failures(result)
    tests_run = mut.COMM_WORLD.allgather(result.testsRun)
    self.assertEqual(0, tests_run.pop(0))
    self.assertIn(1, tests_run)
    tests_run.remove(1)
    self.assertTrue(all(20 == count for count in tests_run))

