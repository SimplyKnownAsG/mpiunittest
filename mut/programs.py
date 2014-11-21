
from __future__ import absolute_import

import sys
from unittest import main as TestProgram
from unittest import loader
from unittest import runner
import traceback

import mut
from . import actions
from . import suites
from . import results
from . import runners

class MpiTestProgram(TestProgram):

  def __init__(self, argv):
    loader.TestLoader.suiteClass = suites.MpiTestSuite
    try:
      if mut.COMM_WORLD.bcast('hi', root=0) != 'hi':
        raise Exception('Could not sync up')
      TestProgram.__init__(self,
                           exit=False,
                           testRunner=runners.MpiTestRunner,
                           argv=argv)
    except Exception as ee:
      print('Something bad happened on {}!'.format(mut.RANK))
      traceback.print_exc()
      if mut.SIZE > 0:
        print('Killing the rest of MPI!')
        mut.COMM_WORLD.Abort(-1)
 