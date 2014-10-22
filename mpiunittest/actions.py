
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
