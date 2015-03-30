
from __future__ import absolute_import

from mut.decorators import *

from mpi4py import MPI

MPI_WORLD = MPI.COMM_WORLD
DISPATCHER_COMM = None
DISPATCHER_TAG = 424242
RANK = MPI_WORLD.Get_rank()
SIZE = MPI_WORLD.Get_size()
DISPATCHER_RANK = 0


def main():
    from mut.__main__ import get_test_program
    get_test_program()


def mpi_flatten_gather(iterable):
    '''Performs an MPI gather operation for a series of iterables. A flattened
    list is returned for the master node, worker nodes are returned the original
    object
    '''
    it_of_its = MPI.COMM_WORLD.gather(iterable, root=0)
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
    lengths = MPI.COMM_WORLD.gather(length, root=0)
    if RANK == 0:
        return sum(lengths)
    else:
        return length


def take_over_the_world():
    '''
    they're pinky and the brain
    yes, pinky and the brain
    one is a genius
    the other's insane.
    they're laboratory mice
    their genes have been spliced
    they're dinky
    they're pinky and the brain, brain, brain, brain
    brain, brain, brain, brain
    brain.
    '''
    global DISPATCHER_COMM
    if SIZE < 3:
        raise RuntimeError('Cannot run mut with size < 3, ' 
                           'increase the number of processors to at least 3.')
    elif DISPATCHER_COMM is not None:
        raise RuntimeError('Cannot take over the world twice!')
    MPI.COMM_WORLD = MPI_WORLD.Split(int(RANK == DISPATCHER_RANK))
    DISPATCHER_COMM = MPI_WORLD


def prepare_for_tomorrow_night():
    '''
    Brain: We must prepare for tomorrow night.
    Pinky: Why? What are we going to do tomororw night?
    Brain: The same thing we do every night, Pinky -- try to take over the world!
    '''
    MPI.COMM_WORLD = MPI_WORLD
    global DISPATCHER_COMM
    if DISPATCHER_COMM is not None:
        DISPATCHER_COMM = None

