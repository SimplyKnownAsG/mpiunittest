
from __future__ import absolute_import

import mut

class Action(object):

  def invoke(self):
    raise NotImplementedError()


class StopAction(Action):
  def invoke(self):
    return False


# class MpiFailure(Exception):
#   def __init__(self, rank):
#     Exception.__init__(self,
#                        'An error occurred in process {}.'.format(rank))


class FailureAction(Action):
  
  def __init__(self):
    self._original_rank = mut.RANK

  def invoke(self):
    RequestWorkAction.abort()
    return True


class WaitingAction(Action):
  def invoke(self):
    return True


class MpiActionError(Exception):
  def __init__(self, received_object):
    Exception.__init__(self,
                       'Expected to get Action, but instead received {} of '
                       'type {}.'
                       .format(received_object, type(received_object)))


class BacklogRegistrationError(Exception):
  def __init__(self, received_object):
    Exception.__init__(self,
                       'Expected to add Action to backlog, but instead '
                       'received {} of type {}'
                       .format(received_object, type(received_object)))


class WorkRequestError(Exception):
  def __init__(self, rank):
    Exception.__init__(self, 'Rank {} cannot request work.'.format(rank))


class RequestWorkAction(Action):
  
  _backlog = []
  
  @classmethod
  def add_work(cls, action):
    if not isinstance(action, Action):
      raise BacklogRegistrationError(action)
    cls._backlog.append(action)
  
  @classmethod
  def abort(cls):
    del(cls._backlog[:])

  def __init__(self):
    self.worker_rank = mut.RANK
    if self.worker_rank == 0:
      raise WorkRequestError(self.worker_rank)

  def invoke(self):
    workAction = None
    try:
      workAction = self._backlog.pop(0)
    except IndexError:
      workAction = WaitingAction()
    # print('[{}] id:{} len:{} worker_rank:{}, action:{}'
    #       .format(mut.RANK, id(self._backlog), len(self._backlog), self.worker_rank, workAction))
    mut.COMM_WORLD.send(workAction, dest=self.worker_rank)
    return True
