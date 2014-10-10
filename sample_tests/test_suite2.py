import unittest
import time

class Suite2_0Tests(unittest.TestCase):

  def test_0(self):
    time.sleep(0.0)
    self.assertEqual(0, 0)

  def test_1(self):
    time.sleep(0.5)
    self.assertEqual(1, 1)

class Suite2_1Tests(unittest.TestCase):

  def test_0(self):
    time.sleep(0.0)
    self.assertEqual(0, 0)

  def test_1(self):
    time.sleep(0.5)
    self.assertEqual(1, 1)

