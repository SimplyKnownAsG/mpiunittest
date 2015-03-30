
from __future__ import absolute_import

import traceback

import mut
from mut import programs
from mut import logger

def get_test_program(argv=None):
    return programs.MpiTestProgram(argv)


if __name__ == '__main__':
    test_program = get_test_program()

