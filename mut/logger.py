
from __future__ import absolute_import

import sys
import threading
import traceback

from mpi4py import MPI

import mut
from mut import actions

_stderr = sys.stderr
_stdout = sys.stdout


def _format_message(message):
    lines = message.splitlines()
    prefix = '[mut.{:0>3}] '.format(mut.RANK)
    if any(len(ll) > 0 for ll in lines):
        return '{}{}\n'.format(prefix, ('\n' + prefix).join(lines))
    return None


def log(message):
    msg = _format_message(message)
    if msg is not None:
        msg_action = LogMessageAction(msg)
        msg_action.send()


def write(message):
    if isinstance(message, basestring) and len(message) > 0:
        msg_action = LogMessageAction(message)
        msg_action.send()


def all_log(message):
    messages = mut.DISPATCHER_COMM.gather(_format_message(message), root=0)
    if mut.RANK == mut.DISPATCHER_RANK:
        msg_action = LogMessageAction(''.join(mm for mm in messages if mm is not None))
        msg_action.send()


class LogMessageAction(actions.Action):

    def __init__(self, message):
        self._message = message

    def __reduce__(self):
        return LogMessageAction, (self._message,)

    def invoke(self):
        _stderr.write(self._message)
        return True

    def send(self):
        if mut.RANK == mut.DISPATCHER_RANK:
            self.invoke()
        else:
            mut.DISPATCHER_COMM.send(self,
                                     dest=mut.DISPATCHER_RANK,
                                     tag=mut.DISPATCHER_TAG)

