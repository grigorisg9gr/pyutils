# Copyright (C) 2015 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

import os
import shutil
import errno
import glob

def mkdir_p(path):
    """ 'mkdir -p' in Python. """
    try:  # http://stackoverflow.com/a/11860637/1716869
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


def is_path(path, msg='Not valid path (%s)'):
    """
    Checks if a path exists.
    If it does, it returns True, otherwise it prints a message (msg) and returns False
    """
    if not(os.path.isdir(path)):
        print(msg % path)
        return False
    return True


def rename_files(file_path, ext, initial_suffix='', new_suffix='', pad_digits=6):
    """
    Serialises and renames files following an alphabetical ordering.
    It does this only for the files that match the pattern provided (initial_suffix + ext).
    Then renames (rewrites) those by restarting numbering from 0.
    :param file_path:       Initial path with the files to be renamed.
    :param ext:             Extension of the files that should be renamed (e.g. 'png').
    :param initial_suffix:  (optional) Initial suffix of files before extension.
    :param new_suffix:      (optional) New suffix to the renamed files.
    :param pad_digits:      (optional) Number of digits for padding the new filenames.
    :return:
    """
    if not is_path(file_path):
        return -1
    ext = '.' + ext if ext[0] != '.' else ext
    padding = '%.' + str(int(pad_digits)) + 'd'
    list2rename = sorted(glob.glob(file_path + '*' + initial_suffix + ext))
    for cnt, elem_p in enumerate(list2rename):
        os.rename(elem_p, file_path + padding % cnt + new_suffix + ext)
    return 1


def change_suffix(file_path, ext, initial_suffix='', new_suffix=''):
    """
    Change the suffix in the files in file_path.
    If initial_suffix is provided, only the files that have it will be considered,
    otherwise all files in the path with the specified extension.

    ASSUMPTION : If the symbol '_' exists in a file, then only the last occurrence
    will be considered as part of the filename and will be removed.
    :param file_path:       Initial path with the files to be renamed.
    :param ext:             Extension of the files that should be renamed (e.g. 'png').
    :param initial_suffix:  (optional) Initial suffix of files before extension.
    :param new_suffix:      (optional) New suffix (if '', no suffix will be provided).
    :return:
    """
    if not is_path(file_path):
        return -1
    ext = '.' + ext if ext[0] != '.' else ext
    end1 = initial_suffix + ext
    end_p = len(end1)
    list2rename = sorted(glob.glob(file_path + '*' + end1))
    for cnt, elem_p in enumerate(list2rename):
        elem_n = elem_p[elem_p.rfind('/') + 1:]
        till_pos = -end_p if elem_n.rfind('_') < 0 else elem_n.rfind('_')
        os.rename(elem_p, file_path + elem_n[:till_pos] + new_suffix + ext)
    return 1
