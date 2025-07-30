from typing import Literal

from bear_utils.constants._meta import RichIntEnum, Value

FAILURE: Literal[45] = 45
ERROR: Literal[40] = 40
WARNING: Literal[30] = 30
WARN: Literal[30] = WARNING
INFO: Literal[20] = 20
SUCCESS: Literal[15] = 15
DEBUG: Literal[10] = 10
VERBOSE: Literal[5] = 5
NOTSET: Literal[0] = 0


level_to_name = {
    FAILURE: "FAILURE",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    SUCCESS: "SUCCESS",
    DEBUG: "DEBUG",
    VERBOSE: "VERBOSE",
    NOTSET: "NOTSET",
}

name_to_level = {
    "FAILURE": FAILURE,
    "ERROR": ERROR,
    "WARN": WARNING,
    "WARNING": WARNING,
    "INFO": INFO,
    "SUCCESS": SUCCESS,
    "DEBUG": DEBUG,
    "VERBOSE": VERBOSE,
    "NOTSET": NOTSET,
}


class LogLevel(RichIntEnum):
    """Enumeration for logging levels."""

    NOTSET = Value(NOTSET, "NOTSET")
    VERBOSE = Value(VERBOSE, "VERBOSE")
    DEBUG = Value(DEBUG, "DEBUG")
    INFO = Value(INFO, "INFO")
    WARNING = Value(WARNING, "WARNING")
    ERROR = Value(ERROR, "ERROR")
    FAILURE = Value(FAILURE, "FAILURE")
    SUCCESS = Value(SUCCESS, "SUCCESS")
