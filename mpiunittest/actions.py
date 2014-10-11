
class Action(object):

  def invoke(self):
    raise NotImplementedError()

class StopAction(object):
  def invoke(self):
    return False

