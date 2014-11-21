
from __future__ import absolute_import

import functools
import types
import sys


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
  
  Notes
  -----
  This is only applicable to classes, i.e. cannot be applied to methods.
  '''
  def decorator(test_class):
    if not isinstance(test_class, (type, types.ClassType)):
      raise DecoratorError('slow_test only applies to classes')
    class DecoratedClass(test_class):
      __mut_slow_estimate__ = time_estimate
    return DecoratedClass
  return decorator

