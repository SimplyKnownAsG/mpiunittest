
from __future__ import absolute_import

import functools
import types
import sys
import unittest


class DecoratorError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)


def slow_test(time_estimate=sys.maxint):
    '''Designates a test suite as being slower than others, which will result in it tested first(ish).
    
    :py:code:`time_estimate` is used to determine the order of :py:code:`@slow_tests`. The higher
    the number, the earlier it will be called. It doesn't really matter whether it is an integer or
    float, just so long as it can be compared.
    
    Parameters
    ----------
    time_estimate : numerical
      relative estimate on how long the test will take.
    
    Warning
    -------
    This is only applicable to classes, i.e. cannot be applied to methods.
    '''
    def decorator(test_class):
        if not isinstance(test_class, (type, types.ClassType)):
            raise DecoratorError('@slow_test only applies to classes')
        class DecoratedClass(test_class):
            __mut_slow_estimate__ = time_estimate
        DecoratedClass.__name__ = test_class.__name__
        DecoratedClass.__module__ = test_class.__module__
        return DecoratedClass
    return decorator

def parallel(min_mpi_size=2):
    '''Indicates a test needs to be run by all processors in parallel.
    
    :py:code:`min_mpi_size` is used to determine if the test should run given the actual MPI size;
    if :py:code:`min_mpi_size < mpi4py.MPI.COMM_WORLD.Get_size()`, then the test will be skipped.
    
    Parameters
    ----------
    min_mpi_size : int
      Indicates the minimum MPI size needed to run this test. If MPI size is less than min_mpi_size,
      the test will be skipped.
    
    Warning
    -------
    This is only applicable to classes, i.e. cannot be applied to methods.
    '''
    def decorator(test_class):
        if not isinstance(test_class, (type, types.ClassType)):
            raise DecoratorError('@parallel_test only applies to classes')
        class DecoratedClass(test_class):
            __mut_parallel__ = min_mpi_size
        DecoratedClass.__name__ = test_class.__name__
        DecoratedClass.__module__ = test_class.__module__
        return DecoratedClass
    return decorator
