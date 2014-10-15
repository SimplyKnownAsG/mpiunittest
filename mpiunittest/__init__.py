from __future__ import absolute_import
from __future__ import print_function

from .programs import SerialTestProgram
from .programs import MasterTestProgram
from .programs import WorkerTestProgram

COMM_WORLD = None
RANK = 0
SIZE = 1

def get_test_program():
  try:
    from mpi4py import MPI
    
    global COMM_WORLD, RANK, SIZE
    COMM_WORLD = MPI.COMM_WORLD
    RANK = COMM_WORLD.Get_rank()
    SIZE = COMM_WORLD.Get_size()
  except ImportError as ie:
    pass
  if SIZE <= 2 and RANK == 0:
    return SerialTestProgram()
  elif SIZE > 2 and RANK == 0:
    return MasterTestProgram()
  return WorkerTestProgram()

