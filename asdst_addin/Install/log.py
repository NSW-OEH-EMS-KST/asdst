from __future__ import print_function
from contextlib import contextmanager
from functools import wraps
import logging
import os
import inspect

logger = None


def debug(msg):
    if logger:
        logger.debug(msg)
    else:
        print("DEBUG: " + msg)


def info(msg):
    if logger:
        logger.info(msg)
    else:
        print("INFO: " + msg)


def warn(msg):
    if logger:
        logger.warn(msg)
    else:
        print("WARNING: " + msg)


def error(msg):
    if logger:
        logger.error(msg)
    else:
        print("ERROR: " + msg)


_ADDIN_MESSAGE = print


class ArcStreamHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        # TODO borrow from GG3...
        _ADDIN_MESSAGE(msg)


def configure_logging(log_file, addin_message):

    global _ADDIN_MESSAGE
    _ADDIN_MESSAGE = addin_message

    if not os.path.exists(log_file):
        open(log_file, 'a').close()

    global logger
    logger = logging.getLogger('asdst')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s", datefmt="%Y%m%d %H%M%S")

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.debug("FileHandler added")

    ah = ArcStreamHandler()
    ah.setLevel(logging.INFO)
    logger.addHandler(ah)
    logger.debug("ArcLogHandler added")

    logger.debug("Logging configured")
    # print("Logging configured")

    return


@contextmanager
def error_trap(identifier=None):
    """ A context manager that traps and logs exception in its block.
        Usage:
        with error_trapping('optional description'):
            might_raise_exception()
        this_will_always_be_called()
    """
    identifier = identifier or inspect.getframeinfo(inspect.currentframe())[2]
    _in = "IN  " + identifier
    _out = "OUT " + identifier

    if not logger:
        say = print
        err = print
    else:
        say = logger.debug
        err = logger.error

    try:
        say(_in)
        yield
        say(_out)
    except Exception as e:
        err(str(e))

    return


def log(f):
    """ A decorator to trap and log exceptions """
    @wraps(f)
    def wrapper(*args, **kwargs):
        with error_trap(f.__name__):
                return f(*args, **kwargs)

    return wrapper


def main():
    pass

if __name__ == '__main__':
    main()
