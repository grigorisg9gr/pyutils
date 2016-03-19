# Copyright (C) 2015 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

import os
from os.path import isdir, isfile, sep, join
import shutil
import errno
import glob


def mkdir_p(path):
    """ 'mkdir -p' in Python. """
    try:  # http://stackoverflow.com/a/11860637/1716869
        os.makedirs(path)
        return path
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and isdir(path):
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


def is_path(path, msg=None, stop_execution=False):
    """
    Checks if a path exists.
    :param path:            Path to be checked.
    :param msg:             (optional) Message that will be printed in case it does not exist.
    :param stop_execution:  (optional) Boolean to declare if we want to stop execution if
    the path does not exist. If True, then a RuntimeError will be raised, the function will return False.
    :return:                Boolean value. True if the path exists, False otherwise.
    """
    if not(isdir(path)):
        if msg is None:
            msg = 'Not valid path ({})'.format(path)
        if stop_execution:
            raise RuntimeError(msg)
        print(msg)
        return False
    return True


def rename_files(file_path, ext, initial_suffix='', new_suffix='', pad_digits=6, starting_elem=0):
    """
    Serialises and renames files following an alphabetical ordering.
    It does this only for the files that match the pattern provided (initial_suffix + ext).
    Then renames (rewrites) those by restarting numbering from 0.
    :param file_path:       Initial path with the files to be renamed.
    :param ext:             Extension of the files that should be renamed (e.g. 'png').
    :param initial_suffix:  (optional) Initial suffix of files before extension.
    :param new_suffix:      (optional) New suffix to the renamed files.
    :param pad_digits:      (optional) Number of digits for padding the new filenames.
    :param starting_elem:    (optional) First element name, by default zero_based.
    Should be int, smaller than 10.
    :return:
    """
    if not isdir(file_path):
        return -1
    if starting_elem < 0:
        print('Cannot start from negative numbering, converting to positive.')
        starting_elem = -starting_elem
    file_path = join(file_path, '')  # add a separator if non exists.
    ext = '.' + ext if ext[0] != '.' else ext
    padding = '%.' + str(int(pad_digits)) + 'd'
    list2rename = sorted(glob.glob(file_path + '*' + initial_suffix + ext))
    for cnt, elem_p in enumerate(list2rename):
        os.rename(elem_p, file_path + padding % (cnt + starting_elem) + new_suffix + ext)
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
    if not isdir(file_path):
        return -1
    file_path = join(file_path, '')  # add a separator if non exists.
    ext = '.' + ext if ext[0] != '.' else ext
    end1 = initial_suffix + ext
    end_p = len(end1)
    list2rename = sorted(glob.glob(file_path + '*' + end1))
    for cnt, elem_p in enumerate(list2rename):
        elem_n = elem_p[elem_p.rfind('/') + 1:]
        till_pos = -end_p if elem_n.rfind('_') < 0 else elem_n.rfind('_')
        os.rename(elem_p, file_path + elem_n[:till_pos] + new_suffix + ext)
    return 1


def remove_empty_paths(path, removeRoot=False, verbose=True):
    """
    Removes empty folders recursively.
    It searches for empty sub-folders, deletes them and then searches the initial path.
    :param path:         Initial path to remove empty (sub-)folders.
    :param removeRoot:  (optional) Boolean, if True, removes the initial path if empty.
    :param verbose:     (optional) Boolean, if True, prints info during execution.
    :return:
    """
    # code similar to: http://www.jacobtomlinson.co.uk/2014/02/16/python-script-recursively-remove-empty-folders-directories/
    if not isdir(path):
        if verbose:
            print('The path {} does not exist.'.format(path))
        return

    # recursively check for empty sub-folders and delete them if they are empty.
    file_list = os.listdir(path)
    if len(file_list):
        for f in file_list:
            new_path = join(path, f)
            if isdir(new_path):
                remove_empty_paths(new_path, removeRoot=True)

    # if the (initial) folder is empty, delete it.
    file_list = os.listdir(path)
    if len(file_list) == 0 and removeRoot:
        if verbose:
            print('Removing the empty path: {}.'.format(path))
        os.rmdir(path)


def copy_contents_of_folder(src, dest):
    """
    Performs the unix command of 'cp -r [path_0]/* [path_1]'.
    :param src: (str) Path to copy from.
    :param dest: (str) Path to copy to.
    :return:
    """
    assert(isdir(src))
    sepq = os.path.sep
    os.system('cp -r {}{}* {}'.format(src, sepq, dest))
