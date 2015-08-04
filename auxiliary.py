import os
import inspect


def whoami():
    """
    Name of a function returned as a string.
    """
    return inspect.stack()[1][3]


def whosparent():
    """
    Name of the caller of a function.
    """
    # http://stefaanlippens.net/python_inspect
    return inspect.stack()[2][3]
