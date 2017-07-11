from __future__ import print_function
from contextlib import contextmanager
from functools import wraps
import logging
import os
import inspect
import utils


logger = None


def get_log_file_and_path():

    return os.path.join(utils.get_appdata_path(), "asdst.log")


def debug(msg):

    if not logger:
        configure_logging()

    try:
        logger.debug(msg)
    except:
        print("DEBUG: " + msg)


def info(msg):

    if not logger:
        configure_logging()

    try:
        logger.info(msg)
    except:
        print("INFO: " + msg)


def warn(msg):

    if not logger:
        configure_logging()

    try:
        logger.warn(msg)
    except:
        print("WARNING: " + msg)


def error(msg):

    if not logger:
        configure_logging()

    try:
        logger.error(msg)
    except:
        print("ERROR: " + msg)


class ArcStreamHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        # TODO borrow from GG3...
        # _ADDIN_MESSAGE(msg)


def configure_logging():  # log_file, addin_message):

    log_file = get_log_file_and_path()

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
        configure_logging()

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

