
from __future__ import absolute_import, print_function

import unittest
import os
import glob

import mut
from mut import __main__ as lion_mane
from mut import programs

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
      for test_file in glob.glob(SuiteWriter.file_prefix + '*'):
        os.remove(test_file)

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
    if mut.RANK == 0:
      sw = SuiteWriter(mut.SIZE - 1, 10, 0.1)
      sw.write()
    program = lion_mane.get_test_program(['mut', 'discover', '-bvp', 'sample_*.py'])
    result = program.result
    self._check_results_for_failures(result)
    self.assertEqual(result.testsRun, 10 if mut.RANK > 0 else 0)

  @unittest.skip('i do whut i waunt')
  def test_unequalDistribution(self):
    if mut.RANK == 0:
      sw = SuiteWriter(mut.SIZE - 2, 20, 5.0)
      sw.write()
      sw = SuiteWriter(1, 1, 5.0)
      sw.write()
    program = lion_mane.get_test_program(['mut', 'discover', '-bvp', 'sample_*.py'])
    result = program.result
    self._check_results_for_failures(result)
    tests_run = mut.COMM_WORLD.allgather(result.testsRun)
    self.assertEqual(0, tests_run.pop(0))
    self.assertIn(1, tests_run)
    tests_run.remove(1)
    self.assertIn(0, tests_run)
    tests_run.remove(0)
    self.assertTrue(all(20 == count for count in tests_run))
    self.assertEqual(result.testsRun, 10 if mut.RANK > 0 else 0)

class SuiteWriter(object):
  
  file_prefix = 'sample_'
  _file_num = 0
  
  def __init__(self, num_suites, tests_per_suite, seconds_per_suite):
    self._num_suites = num_suites
    self._tests_per_suite = tests_per_suite
    self._seconds_per_suite = seconds_per_suite
    self._stream = None
  
  def write(self):
    SuiteWriter._file_num += 1
    with open('{}suite{}.py'.format(self.file_prefix, self._file_num), 'w') as stream:
      self._stream = stream
      self._write_imports()
      self._write_suites()

  def _write_imports(self):
    self._stream.write('import unittest\n')
    self._stream.write('import time\n')
    self._stream.write('\n')
  
  def _write_suites(self):
    for nn in range(self._num_suites):
      self._stream.write('class Suite{0}_{0}Tests(unittest.TestCase):\n'.format(nn))
      self._stream.write('\n')
      self._write_tests()
  
  def _write_tests(self):
    time_per_test = float(self._seconds_per_suite) / self._tests_per_suite
    for ii in range(self._tests_per_suite):
      self._stream.write('  def test_{}(self):\n'.format(ii))
      self._stream.write('    time.sleep({})\n'.format(time_per_test))
      self._stream.write('    self.assertEqual({0}, {0})\n'.format(ii))
      self._stream.write('\n')

def write_long_tests():
  with open('sample_long.py', 'w') as stream:
    stream.write('import unittest\n')
    stream.write('import time\n')
    stream.write('\n')
    stream.write('class LongTestSuite(unittest.TestCase):\n')
    write_test_cases(stream, 10, 3)
 
def write_test_cases(stream, number, mult=0.1):
  for tt in range(number):
    stream.write('  def test_{}(self):\n'.format(tt))
    stream.write('    time.sleep({:.3f})\n'.format(mult * tt / number))
    stream.write('    self.assertEqual({0}, {0})\n'.format(tt))
    stream.write('\n')

def write_failure_tests(): 
  with open('sample_errors_and_failures.py', 'w') as stream:
    stream.write('''import unittest

class TestErrors(unittest.TestCase):
  def test_error(self):
    raise Exception('this is intentional!')


class TestFailures(unittest.TestCase):
  def test_fails(self):
    self.assertEqual(1, 2, 'intentional failure')


class TestPasses(unittest.TestCase):
  def test_passes(self):
    self.assertEqual(1, 1)


class SetUpError(TestPasses):
  def setUp(self):
    raise Exception('Intentional exception')


class SetUpClassError(TestPasses):
  @classmethod
  def setUpClass(cls):
    raise Exception('Intentional exception')


class TearDownError(TestPasses):
  def tearDown(self):
    raise Exception('Intentional exception')


class TearDownClassError(TestPasses):
  @classmethod
  def tearDownClass(cls):
    raise Exception('Intentional exception')
''')


