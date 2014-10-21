
COMM_WORLD = None
RANK = 0
SIZE = 1

try:
  from mpi4py import MPI
  
  COMM_WORLD = MPI.COMM_WORLD
  RANK = COMM_WORLD.Get_rank()
  SIZE = COMM_WORLD.Get_size()
except ImportError as ie:
  pass
