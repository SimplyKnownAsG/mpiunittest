
from __future__ import absolute_import

import traceback

import mut
from . import programs
from . import logger

def get_test_program(argv=None):
    try:
        logger.start_log_thread()
        if mut.SIZE <= 2 and mut.RANK == 0:
            print('Running in series, because there are not enough child-processes.')
            return programs.SerialTestProgram(argv=argv)
        elif mut.SIZE > 2 and mut.RANK == 0:
            print('Running in parallel.')
        #logger.log('I guess this is working')
        return programs.MpiTestProgram(argv)
    finally:
        logger.stop_log_thread()


if __name__ == '__main__':
    test_program = get_test_program()
