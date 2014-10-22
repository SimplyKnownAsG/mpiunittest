
from __future__ import absolute_import

import mpiunittest as mut

class Action(object):

  def invoke(self):
    raise NotImplementedError()


class StopAction(Action):
  def invoke(self):
    return False


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
  
  def __init__(self):
    self.worker_rank = mut.RANK
    if self.worker_rank == 0:
      raise WorkRequestError(self.worker_rank)

  def invoke(self):
    workAction = None
    try:
      workAction = self._backlog.pop(0)
    except IndexError:
      workAction = StopAction()
    print('[{}] id:{} len:{} worker_rank:{}, action:{}'
          .format(mut.RANK, id(self._backlog), len(self._backlog), self.worker_rank, workAction))
    mut.COMM_WORLD.send(workAction, dest=self.worker_rank)
    return True
