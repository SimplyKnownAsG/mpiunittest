
from __future__ import absolute_import

from .decorators import *

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

def mpi_flatten_gather(iterable):
  '''Performs an MPI gather operation for a series of iterables. A flattened
  list is returned for the master node, worker nodes are returned the original
  object
  '''
  it_of_its = COMM_WORLD.gather(iterable, root=0)
  if RANK == 0:
    return [ii for ii_col in it_of_its for ii in ii_col]
  else:
    return iterable

def mpi_length(iterable):
  '''Peforms an MPI gather operation which returns the length of all items. For
  the master node this is the sum of all lengths, the worker nodes will get the
  length of their own iterable.
  '''
  length = len(iterable)
  lengths = COMM_WORLD.gather(length, root=0)
  if RANK == 0:
    return sum(lengths)
  else:
    return length

def mpi_log(stream, content):
  prefix = '[mut.{:0>3}] '.format(RANK)
  lines = content.splitlines()
  if any(len(ll) > 0 for ll in lines):
    msg = '{}{}\n'.format(prefix, ('\n' + prefix).join(lines))
  else:
    msg = ''
  messages = COMM_WORLD.gather(msg, root=0)
  if RANK == 0:
    for msg in [mm for mm in messages if mm != '']:
      stream.write(msg)
