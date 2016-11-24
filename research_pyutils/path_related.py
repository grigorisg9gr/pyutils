# Copyright (C) 2015 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

import os
from os.path import isdir, isfile, sep, join
import shutil
import errno
from glob import glob
from subprocess import check_output
from subprocess import check_output

# TO-DO: put progress bars in all the packages with time-consuming loops.

def mkdir_p(path, mode=500):
    """ 'mkdir -p' in Python. """
    try:  # http://stackoverflow.com/a/11860637/1716869
        os.makedirs(path, mode=mode)
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


def copy_contents_of_folder(src, dest, suffix=''):
    """
    Performs the unix command of 'cp -r [path_0]/*[suffix] [path_1]'.
    :param src: (str) Path to copy from.
    :param dest: (str) Path to copy to.
    :param suffix: (Optional, str) The suffix/extension of the files.
    :return:
    """
    assert(isdir(src))
    sepq = os.path.sep
    os.system('cp -r {}{}*{} {}'.format(src, sepq, suffix, dest))


def _get_stem(el):
    # aux function.
    return el[:el.rfind('.')]

def _format_string_name_number(pad, name):
    return '{nam1:0{pad}d}'.format(pad=pad, nam1=name)

def _check_or_initialise(el, l, idx, assertion=False):
    """
    Auxiliary function. It checks whether el is part of the list l,
    otherwise it initialiases it to l[idx].
    It returns the int of the stem name of the file.
    :param el: (None or string) Part of the list l if not None.
    :param l:  (list) List of elements.
    :param idx: (int) Index in case el is None.
    :param assertion: (Bool, optional) Raise assertion error if el
           is not in list l.
    :return:
    """
    assert(isinstance(l, list))
    if el is None:
        el = l[idx]
    elif assertion:
        assert(el in l)
    return int(_get_stem(el))


def copy_the_previous_if_missing(p, init_fr=None, last_fr=None, verbose=False):
    """
    Copies the previous file if it is missing. The result of this function
    creates a sequential structure of files, starting from the first one till
    the final one. Works in a folder with files.
    It sequentially tries to access the files and if they are missing, it copies
    the previous one.
    ASSUMPTIONS:
      a) The naming should be only numbers, e.g. '000034.[suffix]',
      b) The [suffix] of the first file (listdir) will be copied in case
         of a missing file.

    :param p:  (string) Base path for performing the copying/checking.
    :param init_fr: (string, optional) Initial filename to start the
           checking from. It should exist in the dir p.
    :param last_fr: (string, optional) Final filename to end the checking.
           As with the init_fr, it should exist in the dir p.
    :param verbose: (Bool, optional) Whether to print info about which
           frames are copied.
    :return:
    """
    from pathlib import Path
    from shutil import copy2
    assert(isdir(p))
    l = sorted(os.listdir(p))
    # Gets the init_fr. If provided, it verifies that this is indeed included
    # in the provided listdir in the path. If it None, then the init_fr is
    # assumed to be the first filename in the listdir.
    # If NOT provided, then no files before the l[0] are copied, e.g. if
    # 03.p is the first file, then the 01.p or 02.p are not created.
    init_fr = _check_or_initialise(init_fr, l, 0)
    # Similarly for the last_fr.
    last_fr = _check_or_initialise(last_fr, l, -1)
    # get an expected list based on init, last filenames.
    l_run = list(range(init_fr, last_fr + 1))
    ll, lr = len(l), len(l_run)
    assert(lr < 100000)  # ensure that it's not infinite.
    if lr == ll or ll == 0:
        return
    # iterator over the 'real' files list (cnt_l). This might be
    # different than the expected filenames' list, thus a different
    # counter is required.
    cnt_l = 0
    suffix = Path(l[cnt_l]).suffix
    # prune the 'real' list if required. That is, if the first element is
    # not the 'real' first element in the path, we should prune the list.
    c1 = _format_string_name_number(len(l[0]) - len(suffix), init_fr)
    idx = l.index(c1 + suffix)
    if idx > 0:
        l = l[idx :]

    # iterate over the expected elements
    for cn, el in enumerate(l_run):
        # get the actual name of the l files (i.e. dump the suffix).
        nam = _get_stem(l[cnt_l])
        if el == int(nam):
            cnt_l += 1
        else:
            # missing file, copy previous
            if cnt_l > 0:
                prev = el - 1
            else:
                prev = int(nam)
            # format the names of previous and new, based on the correct padding.
            name_pr = _format_string_name_number(len(nam), prev)
            name = _format_string_name_number(len(nam), el)
            # format the filenames paths for the new (i.e. to be copied) and
            # old (i.e. to copy)files.
            p_n = p + name + suffix
            p_o = p + name_pr + suffix
            assert(isfile(p_o) and not isfile(p_n))
            if verbose:
                print('Copying the file {} to the {}.'.format(p_o, p_n))
            copy2(p_o, p_n)

        if cnt_l == ll and cnt_l > 0:
            # in that case, we reached the end of the 'real' files list, however
            # the 'destination' is not achieved in the expected filenames.
            # Hence, one new dummy element is appended, so that it
            # copies the rest of the files.
            l.append(_format_string_name_number(len(nam), 100000) + suffix)


def unzip_all_dir(p, extension='zip'):
    """
    Unzips all the zip folders in the directory.
    :param p: (string) Path with all the zips.
    :param extension: (string, optional) The extension/compressed format 
           of the files.
    :return: None
    """
    from zipfile import ZipFile
    import tarfile
    m = 'There is no such path with zips (p = {}).'
    assert isdir(p), m.format(p)
    all_zips = glob(join(p, '*.{}'.format(extension)))
    for zi in all_zips:
        if extension == 'zip':
           compr_ref = ZipFile(zi, 'r')
        else:
           # right now only these two formats supported.
           compr_ref = tarfile.open(zi, 'r')
        compr_ref.extractall(p)
        compr_ref.close()


def count_files(path='.', ending='', directory=False, subdirs=False):
    """
    It counts the files in the current directory and the subfolders.
    There is the options to count only in the current directory (and
    not in the subfolders), or to count only files with certain extensions.

    :param path:   (string, optional) The base path to count the files in.
    :param ending: (string, optional) The extension/suffix of the files
        to search for. Only makes sense if directory=False.
    :param directory: (string, optional) If True, then it *only* counts the
        number of directories (folders). The called one is also counted.
        If False, then it just counts the files.
    :param subdirs: (string, optional) If False, it counts only in this
        directory and not the subfolders. If True, it recursively counts
        the files in the subfolders as well.
    :return: (int) The number of files.
    """
    assert isdir(path), 'The initial path does not exist.'
    if not subdirs:
        # in this case, we just care for the first
        # level, apply the fastest method.
        if ending == '':
            cmd = 'ls -f {} | wc -l'.format(path)
        else:
            # This is a workaround because ls -f [path]/* returns also
            # the results of subfolders.
            cmd = 'ls -f {}*{} | wc -l'.format(path, ending)
    else:
        add_arg = ''
        if directory:
            add_arg = ' -type d '
        cmd = 'find {}{} -name "*{}" -print | wc -l'.format(path, add_arg, ending)
    nr_files = check_output(cmd, shell=True)
    # get rid of the \n in the end and return.
    return int(nr_files[:-1])
