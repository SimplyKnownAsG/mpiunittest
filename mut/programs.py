
from __future__ import absolute_import

from unittest import main as TestProgram
from unittest import loader
import traceback

import mut
from mut import suites
from mut import runners

class MpiTestProgram(TestProgram):

    def __init__(self, argv):
        loader.TestLoader.suiteClass = suites.MpiTestSuite
        try:
            mut.take_over_the_world()
            if mut.DISPATCHER_COMM.bcast('hi', root=0) != 'hi':
                raise Exception('Could not sync up')
            TestProgram.__init__(self,
                                 exit=False,
                                 testRunner=runners.MpiTestRunner,
                                 argv=argv)
        except Exception as ee:
            print('Something bad happened on {}!'.format(mut.RANK))
            traceback.print_exc()
            print('Killing the rest of MPI!')
            mut.MPI_WORLD.Abort(-1)
        finally:
            mut.prepare_for_tomorrow_night()

