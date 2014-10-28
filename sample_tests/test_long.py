import unittest
import time

class LongTestSuite(unittest.TestCase):
  def test_0(self):
    time.sleep(0.000)
    self.assertEqual(0, 0)

  def test_1(self):
    time.sleep(0.000)
    self.assertEqual(1, 1)

  def test_2(self):
    time.sleep(0.000)
    self.assertEqual(2, 2)

  def test_3(self):
    time.sleep(0.000)
    self.assertEqual(3, 3)

  def test_4(self):
    time.sleep(1.000)
    self.assertEqual(4, 4)

  def test_5(self):
    time.sleep(1.000)
    self.assertEqual(5, 5)

  def test_6(self):
    time.sleep(1.000)
    self.assertEqual(6, 6)

  def test_7(self):
    time.sleep(2.000)
    self.assertEqual(7, 7)

  def test_8(self):
    time.sleep(2.000)
    self.assertEqual(8, 8)

  def test_9(self):
    time.sleep(2.000)
    self.assertEqual(9, 9)

