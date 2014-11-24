
from __future__ import absolute_import

import traceback

import mut
from . import programs

def get_test_program(argv=None):
    if mut.SIZE <= 2 and mut.RANK == 0:
        print('Running in series, because there are not enough child-processes.')
        return programs.SerialTestProgram(argv=argv)
    elif mut.SIZE > 2 and mut.RANK == 0:
        print('Running in parallel.')
    return programs.MpiTestProgram(argv)


if __name__ == '__main__':
    test_program = get_test_program()
