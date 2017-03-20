from __future__ import print_function
from contextlib import contextmanager
from functools import wraps
import logging
import os
import inspect

logger = None

# DEBUG = logging.DEBUG
# INFO = logging.INFO
# debug = None
# info = None
# error = None
# warn = None

def debug(msg):
    if logger:
        logger.debug(msg)


def info(msg):
    if logger:
        logger.info(msg)


def warn(msg):
    if logger:
        logger.warn(msg)


def error(msg):
    if logger:
        logger.error(msg)


# _LEVEL = None
_ADDIN_MESSAGE = print
_CONFIGURED = False


class ArcLogHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        _ADDIN_MESSAGE(msg)


def configure_logging(log_file, addin_message):
    # print("configure_logging {}".format(locals()))

    global _ADDIN_MESSAGE
    _ADDIN_MESSAGE = addin_message

    # try:
    if not os.path.exists(log_file):
        # print("creating log")
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

    ah = ArcLogHandler()
    ah.setLevel(logging.INFO)
    logger.addHandler(ah)
    logger.debug("ArcLogHandler added")

    logger.debug("Logging configured")
    print("Logging configured")

    return


@contextmanager
def error_trapping(identifier=None):
    """ A context manager that traps and logs exception in its block.
        Usage:
        with error_trapping('optional description'):
            might_raise_exception()
        this_will_always_be_called()
    """
    if not logger:
        print("Logging is not configured")
        yield
    else:
        identifier = identifier or inspect.getframeinfo(inspect.currentframe())[2]
        try:
            logger.debug(identifier + " IN")
            yield
            logger.debug(identifier + " OUT")
        except Exception as e:
            logger.error(e, exc_info=True)

    return


def log(f):
    """ A decorator to trap and log exceptions """
    @wraps(f)
    def wrapper(*args, **kwargs):
        with error_trapping(f.__name__):
                return f(*args, **kwargs)

    return wrapper


def main():
    pass

if __name__ == '__main__':
    main()
