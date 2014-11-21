
import mut

class SuiteWriter(object):
  
  file_prefix = 'sample_'
  _file_num = 0
  
  def __init__(self, num_suites, tests_per_suite, seconds_per_suite):
    self._num_suites = num_suites
    self._tests_per_suite = tests_per_suite
    self._seconds_per_suite = seconds_per_suite
    self._stream = None
    self._decorators = []
  
  def write(self):
    if mut.RANK == 0:
      SuiteWriter._file_num += 1
      with open('{}suite{}.py'.format(self.file_prefix, self._file_num), 'w') as stream:
        self._stream = stream
        self._write_imports()
        self._write_suites()

  def _write_imports(self):
    self._stream.write('import unittest\n')
    self._stream.write('import time\n')
    if any(self._decorators):
      self._stream.write('import mut\n')
    self._stream.write('\n')
  
  def _write_suites(self):
    for nn in range(self._num_suites):
      for decorator in self._decorators:
        self._stream.write('{}\n'.format(decorator))
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

  def add_decorator(self, string):
    self._decorators.append(string)

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

