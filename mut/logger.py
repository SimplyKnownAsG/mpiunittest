
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
    if mut.RANK == MUT_LOG_PROCESSOR:
        global _log_thread
        _log_thread = LogThread()
        _log_thread.start()


def stop_log_thread():
    mut.COMM_WORLD.Barrier()
    if mut.RANK == MUT_LOG_PROCESSOR:
        mut.COMM_WORLD.isend(actions.StopAction(), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)
        while _log_thread.is_alive():
            print('waiting for log thread to die')


def _format_message(message):
    lines = message.splitlines()
    prefix = '[mut.{:0>3}] '.format(mut.RANK)
    if any(len(ll) > 0 for ll in lines):
        return '{}{}\n'.format(prefix, ('\n' + prefix).join(lines))
    return None


def log(message):
    msg = _format_message(message)
    if msg is not None:
        mut.COMM_WORLD.isend(LogMessageAction(msg), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)


def write(message):
    if isinstance(message, basestring) and len(message) > 0:
        mut.COMM_WORLD.isend(LogMessageAction(message), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)

def all_log(message):
    messages = mut.COMM_WORLD.gather(_format_message(message + '\n'), root=MUT_LOG_PROCESSOR)
    if mut.RANK == MUT_LOG_PROCESSOR:
        msg = ''.join(messages)
        mut.COMM_WORLD.isend(LogMessageAction(msg), dest=MUT_LOG_PROCESSOR, tag=_MUT_LOG_TAG)


class LogThread(threading.Thread):

    def run(self):
        _stderr.write(_format_message('starting logging thread.'))
        try:
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
        except Exception as shit:
            _stderr.write(_format_message('Something bad happened while receiving message from {}.'
                                          .format(rank)))
            for cc in shit.message:
                _stderr.write(_format_message('{} == {}'.format(cc, ord(cc))))
            _stderr.write(_format_message('Exception: {}\n'.format(shit)))
            stack = traceback.format_exc()
            _stderr.write(_format_message(stack))
            mut.COMM_WORLD.Abort(-1)
        _stderr.write(_format_message('stopping logging thread.\n'))


class LogMessageAction(actions.Action):
    def __init__(self, message):
        self._message = message

    def invoke(self):
        _stderr.write(self._message)
        return True


if __name__ == '__main__':
    try:
        _stdout.write(_format_message('about to start thread'))
        start_log_thread()
        _stdout.write(_format_message('about to log message'))
        log('howdy!')
        _stdout.write(_format_message('just logged message'))
    finally:
        _stdout.write(_format_message('stopping the log thread'))
        stop_log_thread()

