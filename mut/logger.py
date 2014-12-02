
from __future__ import absolute_import

import sys
import threading

import mut
from mut import actions

_MUT_LOG_TAG = 424242
MUT_LOG_PROCESSOR = 0
_log_thread = None
_stderr = sys.stderr
_stdout = sys.stdout

def start_log_thread():
    if mut.RANK == MUT_LOG_PROCESSOR:
        global _log_thread
        _log_thread = LogThread()
        _log_thread.start()


def stop_log_thread():
    if mut.RANK == MUT_LOG_PROCESSOR:
        mut.COMM_WORLD.isend(actions.StopAction(), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)


def log(msg):
    message = '[mut.{:0>3}] {}\n'.format(mut.RANK, msg)
    mut.COMM_WORLD.isend(LogMessageAction(message), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)


class LogThread(threading.Thread):

    def run(self):
        _stderr.write('[mut.{:0>3}] starting logging thread.\n'.format(mut.RANK))
        not_done = True
        while not_done:
            for rank in range(mut.SIZE):
                if not mut.COMM_WORLD.Iprobe(source=rank, tag=_MUT_LOG_TAG):
                    continue
                mpi_action = mut.COMM_WORLD.recv(source=rank, tag=_MUT_LOG_TAG)
                if not isinstance(mpi_action, actions.Action):
                    raise actions.MpiActionError(mpi_action)
                not_done = mpi_action.invoke()
                if not not_done:
                    break
        _stderr.write('[mut.{:0>3}] stopping logging thread.\n'.format(mut.RANK))


class LogMessageAction(actions.Action):
    def __init__(self, message):
        self._message = message

    def invoke(self):
        _stderr.write(self._message)
        return True
