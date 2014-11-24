
from __future__ import absolute_import

import glob
import os
import unittest

import mut
from . import suite_writers

class BaseTest(unittest.TestCase):
 
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
    
    def check_results_for_failures(self, result):
        self.assertEqual(len(result.expectedFailures), 0)
        self.assertEqual(len(result.failures), 0)
        self.assertEqual(len(result.skipped), 0)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.unexpectedSuccesses), 0)
        self.assertEqual(result.wasSuccessful(), True)
    
    def tearDown(self):
        self.tearDownClass()
    
    def setUp(self):
        self.tearDownClass()
        if mut.COMM_WORLD.bcast('hi', root=0) != 'hi':
            raise Exception('Could not sync up')
