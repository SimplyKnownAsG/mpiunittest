
def write_suite(number):
  with open('test_suite{}.py'.format(number), 'w') as stream:
    stream.write('import unittest\n')
    stream.write('import time\n')
    stream.write('\n')
    write_test_suite(stream, number)

def write_test_suite(stream, number):
  for ss in range(number):
    stream.write('class Suite{}_{}Tests(unittest.TestCase):\n'
                 .format(number, ss))
    stream.write('\n')
    write_test_cases(stream, number)

def write_test_cases(stream, number, mult=0.1):
  for tt in range(number):
    stream.write('  def test_{}(self):\n'.format(tt))
    stream.write('    time.sleep({:.3f})\n'.format(mult * tt / number))
    stream.write('    self.assertEqual({0}, {0})\n'.format(tt))
    stream.write('\n')
 
if __name__ == '__main__':
  for nn in range(10):
    write_suite(nn)
  with open('test_long.py', 'w') as stream:
    stream.write('import unittest\n')
    stream.write('import time\n')
    stream.write('\n')
    stream.write('class LongTestSuite(unittest.TestCase):\n')
    write_test_cases(stream, 10, 3)
  with open('test_errors_and_failures.py', 'w') as stream:
    stream.write('import unittest\n')
    stream.write('''

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


