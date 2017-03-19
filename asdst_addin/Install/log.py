from __future__ import print_function
from contextlib import contextmanager
from functools import wraps
import logging
import os
import inspect

DEBUG = logging.DEBUG
INFO = logging.INFO
debug = logging.debug
info = logging.info
error = logging.error

_LEVEL = None
_ADDIN_MESSAGE = print
_CONFIGURED = False


class ArcLogHandler(logging.StreamHandler):
    def emit(self, record):
        msg = self.format(record)
        _ADDIN_MESSAGE(msg)


def configure_logging(log_file, level, addin_message):
    global _LEVEL, _ADDIN_MESSAGE
    _LEVEL = level
    _ADDIN_MESSAGE = addin_message

    # _ADDIN_MESSAGE(log_file)
    try:
        if not os.path.exists(log_file):
            _ADDIN_MESSAGE("creating log")
            open(log_file, 'a').close()

        logging.basicConfig(filename=log_file, filemode="w", level=_LEVEL,
                            format="%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)s %(message)s",
                            datefmt="%Y%m%d %H%M%S")
        logging.debug("Logging configured")
        ah = ArcLogHandler()
        ah.setLevel(logging.INFO)
        logging.getLogger().addHandler(ah)
        logging.debug("ArcLogHandler added")

        # _ADDIN_MESSAGE("Logging configured??")
    except Exception as e:
        print(e)

    global _CONFIGURED
    _CONFIGURED = True
    logging.debug("_CONFIGURED set {}".format(_CONFIGURED))

    return


@contextmanager
def error_trapping(identifier=None):
    """ A context manager that traps and logs exception in its block.
        Usage:
        with error_trapping('optional description'):
            might_raise_exception()
        this_will_always_be_called()
    """
    if not _CONFIGURED:
        yield
    else:
        identifier = identifier or inspect.getframeinfo(inspect.currentframe())[2]
        try:
            debug(identifier + " IN")
            yield   # None
            debug(identifier + " OUT")
        except Exception as e:
            error(e, exc_info=True)

    return


def log(f):
    """ A decorator to trap and log exceptions """
    @wraps(f)
    def wrapper(*args, **kwargs):
        with error_trapping(f.__name__):
            return f(*args, **kwargs)

    return wrapper
