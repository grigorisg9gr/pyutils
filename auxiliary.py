import os
import sys
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


# temporarily suppress output: http://thesmithfam.org/blog/2012/10/25/temporarily-suppress-console-output-in-python/
from contextlib import contextmanager

@contextmanager
def suppress_stdout():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
