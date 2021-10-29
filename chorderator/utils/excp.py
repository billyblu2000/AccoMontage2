from utils.utils import Logging


def handle_exception(code):
    if code // 100 == 2:
        if code == 201:
            msg = '[Error {e}] Pre-process model cannot be recognized!'
        elif code == 202:
            msg = '[Error {e}] Main model cannot be recognized!'
        else:
            msg = '[Error {e}] Post-process model cannot be recognized!'
        raise ValueError(msg.format(e=code))
    elif code // 100 == 5:
        raise RuntimeError('pre')
    elif code // 100 == 6:
        raise RuntimeError('main')
    elif code // 100 == 7:
        raise RuntimeError('post')
