
from __future__ import absolute_import

import sys
import threading
import traceback

import mut
from mut import actions

_MUT_LOG_TAG = 424242
MUT_LOG_PROCESSOR = 0
_log_thread = None
_stderr = sys.stderr
_stdout = sys.stdout

def start_log_thread():
    if _log_thread is None and mut.RANK == MUT_LOG_PROCESSOR:
        global _log_thread
        _log_thread = LogThread()
        _log_thread.start()


def stop_log_thread():
    mut.COMM_WORLD.isend(actions.StopAction(), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)
    if mut.RANK == MUT_LOG_PROCESSOR:
        global _log_thread
        _log_thread = None


def _format_message(message):
    lines = message.splitlines()
    prefix = '[mut.{:0>3}] '.format(mut.RANK)
    if any(len(ll) > 0 for ll in lines):
        return '{}{}\n'.format(prefix, ('\n' + prefix).join(lines))
    return None


def log(message):
    start_log_thread()
    msg = _format_message(message)
    if msg is not None:
        msg_action = LogMessageAction(msg)
        if mut.RANK == MUT_LOG_PROCESSOR:
            _log_thread.add_backlog(msg_action)
        else:
            mut.COMM_WORLD.send(msg_action, dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)


def write(message):
    if isinstance(message, basestring) and len(message) > 0:
        mut.COMM_WORLD.send(LogMessageAction(message), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)

def all_log(message):
    messages = mut.COMM_WORLD.gather(_format_message(message), root=MUT_LOG_PROCESSOR)
    if mut.RANK == MUT_LOG_PROCESSOR:
        msg = ''.join(mm for mm in messages if mm is not None)
        mut.COMM_WORLD.send(LogMessageAction(msg), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)


class LogThread(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self._local_backlog = []

    def add_backlog(self, message_action):
        self._local_backlog.append(message_action)

    def dump_backlog(self):
        backlog = self._local_backlog
        self._local_backlog = []
        for message_action in backlog:
            message_action.invoke()

    def run(self):
        _stderr.write(_format_message('starting logging thread.'))
        not_done = [True for _ in range(mut.SIZE)]
        try:
            while any(not_done):
                for rank in range(mut.SIZE):
                    if rank == MUT_LOG_PROCESSOR:
                        self.dump_backlog()
                    if not mut.COMM_WORLD.Iprobe(source=rank, tag=_MUT_LOG_TAG):
                        continue
                    mpi_action = mut.COMM_WORLD.recv(source=rank, tag=_MUT_LOG_TAG)
                    if not isinstance(mpi_action, actions.Action):
                        raise actions.MpiActionError(mpi_action)
                    not_done[rank] = mpi_action.invoke()
        except Exception as err:
            _stderr.write(_format_message('Something bad happened while receiving message from {}.'
                                          .format(rank)))
            _stderr.write(_format_message('Exception: {}\n'.format(err)))
            stack = traceback.format_exc()
            _stderr.write(_format_message(stack))
            #mut.COMM_WORLD.Abort(-1)
        _stderr.write(_format_message('stopping logging thread.\n'))


class LogMessageAction(actions.Action):

    def __init__(self, message):
        self._message = message

    def invoke(self):
        _stderr.write(self._message)
        return True


if __name__ == '__main__':
    try:
        start_log_thread()
        log('howdy!')
        log('hi!')
        log('hello!')
        log('goodbye!')
    finally:
        stop_log_thread()

