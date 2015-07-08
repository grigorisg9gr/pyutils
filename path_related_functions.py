# Copyright (C) 2015 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

# mkdir -p in python from http://stackoverflow.com/a/11860637/1716869
import os
import shutil
import errno

def mkdir_p(path):
    """ 'mkdir -p' in Python. """
    try:
        os.makedirs(path)
        return path
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return path
        else:
            raise


def rm_if_exists(path):
    """
    :param path: Path that will be removed (if it exists).
    """
    try:
        shutil.rmtree(path)
    except OSError:
        pass