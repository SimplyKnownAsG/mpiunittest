import unittest


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
