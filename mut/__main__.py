
from __future__ import absolute_import

import traceback

import mut
from . import programs

def get_test_program():
  if mut.SIZE <= 2 and mut.RANK == 0:
    print('Running in series, because there are not enough child-processes.')
    return programs.SerialTestProgram()
  elif mut.SIZE > 2 and mut.RANK == 0:
    print('Running in parallel.')
    return programs.MasterTestProgram()
  return programs.WorkerTestProgram()


if __name__ == '__main__':
  try:
    test_program = get_test_program()
  except Exception as ee:
    print('Something bad happened on {}!'.format(mut.RANK))
    print(ee)
    traceback.print_exc()
    if mut.SIZE > 0:
      print('Killing the rest of MPI!')
      mut.COMM_WORLD.Abort(-1)
    
