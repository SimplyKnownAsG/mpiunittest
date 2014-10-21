from __future__ import absolute_import
from __future__ import print_function

import traceback

import mpiunittest
from mpiunittest.programs import SerialTestProgram
from mpiunittest.programs import MasterTestProgram
from mpiunittest.programs import WorkerTestProgram

def get_test_program():
  if mpiunittest.SIZE <= 2 and mpiunittest.RANK == 0:
    print('Running in series, because there are not enough child-processes.')
    return SerialTestProgram()
  elif mpiunittest.SIZE > 2 and mpiunittest.RANK == 0:
    print('Running in parallel.')
    return MasterTestProgram()
  return WorkerTestProgram()


if __name__ == '__main__':
  try:
    test_program = get_test_program()
  except Exception as ee:
    print('Something bad happened!')
    print(ee)
    traceback.print_exc()
    if mpiunittest.SIZE > 0:
      print('Killing the rest of MPI!')
      mpiunittest.COMM_WORLD.Abort(-1)
    
