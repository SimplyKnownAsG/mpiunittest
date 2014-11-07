
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

  @unittest.skip('not working yet...')
  def test_unequalDistribution2(self):
    if mut.RANK == 0:
      sw = suite_writers.SuiteWriter((mut.SIZE - 2) * 2, 20, 3.0)
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
    self.assertTrue(all(40 == count for count in tests_run))
