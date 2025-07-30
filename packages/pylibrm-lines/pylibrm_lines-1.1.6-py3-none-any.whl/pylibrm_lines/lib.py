"""
This module provides functions to configure LIB rm_lines directly.

While it does wrap the library implementations in a pythonic way,
it does not check for any errors or exceptions that may occur.
However, these are basic functions that shouldn't fail under normal circumstances.
"""

import ctypes
from typing import Callable, Optional

from rm_lines_sys import lib

LOG_FUNCTION_TYPE = Callable[[str], None]
LOG_FUNC: Optional[LOG_FUNCTION_TYPE] = None
ERR_FUNC: Optional[LOG_FUNCTION_TYPE] = None
DEBUG_FUNC: Optional[LOG_FUNCTION_TYPE] = None


@ctypes.CFUNCTYPE(None, ctypes.c_char_p)
def python_log_logger(msg):
    if LOG_FUNC is None:
        pass
    LOG_FUNC(msg.decode('utf-8', errors='replace'))


@ctypes.CFUNCTYPE(None, ctypes.c_char_p)
def python_error_logger(msg):
    if ERR_FUNC is None:
        pass
    ERR_FUNC(msg.decode('utf-8', errors='replace'))


@ctypes.CFUNCTYPE(None, ctypes.c_char_p)
def python_debug_logger(msg):
    if DEBUG_FUNC is None:
        pass
    DEBUG_FUNC(msg.decode('utf-8', errors='replace'))


def set_debug_mode(debug: bool):
    """
    Set the debug mode for the library.
    This will enable both debug logging and debug rendering.

    :param debug: If True, enables debug mode; otherwise, disables it.
    """
    lib.setDebugMode(debug)


def get_debug_mode() -> bool:
    """
    Check if the library is in debug mode.

    :return: True if debug mode is enabled, False otherwise.
    """
    return lib.getDebugMode()


def set_logger(func: LOG_FUNCTION_TYPE):
    """
    Set a custom logging function for the library.

    :param func: A callable that takes a string message as an argument.
    """

    global LOG_FUNC

    LOG_FUNC = func

    lib.setLogger(python_log_logger)


def set_error_logger(func: LOG_FUNCTION_TYPE):
    """
    Set a custom error logging function for the library.

    :param func: A callable that takes a string message as an argument.
    """

    global ERR_FUNC

    ERR_FUNC = func

    lib.setErrorLogger(python_error_logger)


def set_debug_logger(func: LOG_FUNCTION_TYPE):
    """
    Set a custom debug logging function for the library.
    Debug messages are verbose but are only triggered if debug mode is enabled.

    :param func: A callable that takes a string message as an argument.
    """

    global DEBUG_FUNC

    DEBUG_FUNC = func

    lib.setDebugLogger(python_debug_logger)
