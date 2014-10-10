from __future__ import absolute_import
from __future__ import print_function

from .test_programs import SerialTestProgram
from .test_programs import MasterTestProgram
from .test_programs import WorkerTestProgram

COMM_WORLD = None
RANK = 0
SIZE = 1

def get_test_program():
  try:
    from mpi4py.MPI import COMM_WORLD as comm_world
    
    global COMM_WORLD, RANK, SIZE
    COMM_WORLD = comm_world
    RANK = COMM_WORLD.Get_rank()
    SIZE = COMM_WORLD.Get_size()
  except ImportError as ie:
    pass
  if SIZE <= 2 and RANK == 0:
    return SerialTestProgram()
  elif SIZE > 2 and RANK == 0:
    return MasterTestProgram()
  return WorkerTestProgram()

