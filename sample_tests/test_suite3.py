import unittest
import time

class Suite3_0Tests(unittest.TestCase):

  def test_0(self):
    time.sleep(0.0)
    self.assertEqual(0, 0)

  def test_1(self):
    time.sleep(0.3)
    self.assertEqual(1, 1)

  def test_2(self):
    time.sleep(0.7)
    self.assertEqual(2, 2)

class Suite3_1Tests(unittest.TestCase):

  def test_0(self):
    time.sleep(0.0)
    self.assertEqual(0, 0)

  def test_1(self):
    time.sleep(0.3)
    self.assertEqual(1, 1)

  def test_2(self):
    time.sleep(0.7)
    self.assertEqual(2, 2)

class Suite3_2Tests(unittest.TestCase):

  def test_0(self):
    time.sleep(0.0)
    self.assertEqual(0, 0)

  def test_1(self):
    time.sleep(0.3)
    self.assertEqual(1, 1)

  def test_2(self):
    time.sleep(0.7)
    self.assertEqual(2, 2)

