import unittest
import time

class Suite1_0Tests(unittest.TestCase):

  def test_0(self):
    time.sleep(0.000)
    self.assertEqual(0, 0)

