# Copyright (C) 2015 Grigorios G. Chrysos
# available under the terms of the Apache License, Version 2.0

import os
from os import system, listdir
from os.path import isdir, isfile, sep, join
import shutil
import errno
from glob import glob
from subprocess import check_output
from pathlib import Path


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
    if not (isdir(path)):
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
    # code inspired from:
    # http://www.jacobtomlinson.co.uk/2014/02/16/python-script-recursively-remove-empty-folders-directories/
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
                remove_empty_paths(new_path, removeRoot=True, verbose=verbose)

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
    assert (isdir(src))
    system('cp -r {}{}*{} {}'.format(src, sep, suffix, dest))


def _format_string_name_number(pad, name):
    return '{nam1:0{pad}d}'.format(pad=pad, nam1=name)


def copy_the_previous_if_missing(p, expected_list=None, suffix=None, verbose=False):
    """
    Copies the previous file if it is missing. If the expected_list is provided, it
    ensures that all the filenames in the expected list exist in the p path as well.
    Use case: Fill the missing files, e.g. 1st order markov assumption.
    ASSUMPTIONS:
        a) The naming should be only numbers, e.g. '000034.[suffix]',
        b) The [suffix] of the first file (listdir) will be copied in case
            no suffix is provided.
    :param p:       (string) Base path for performing the copying/checking.
    :param expected_list: (list, optional) The list of filenames to ensure that exist.
            If it is not provided, then a sequential structure from the first till the
            last element of the p dir is assumed.
    :param suffix:  (string, optional) The suffix of the files to glob. If None is provided,
            then the extension of the first file is used.
    :param verbose: (bool, optional) Whether to print info for the copying.
    :return:
    """
    from shutil import copy2

    if suffix is None:
        init_l = sorted(listdir(p))
        suffix = Path(init_l[0]).suffix
        if verbose:
            m1 = ('The suffix {} chosen, only the files with this'
                  'suffix will be affected.')
            print(m1.format(suffix))
    # update the init_l list with a glob
    init_l = sorted(glob(p + '*' + suffix))
    assert len(init_l) >= 1
    init_l = [Path(el).stem for el in init_l]

    if expected_list is None:
        # as a workaround, we accept the first and the last element
        # we find in the original list and then we just form the
        # expected list with those.
        end_el = int(init_l[-1])
        start_el = int(init_l[0])
        # get the number of digits from the length of the start_el.
        pad = len(init_l[0])
        # format the expected list now.
        expected_list = [_format_string_name_number(pad, el)
                         for el in range(start_el, end_el)]
    else:
        # ensure that there is no extension in the list provided.
        try:
            int(expected_list[0])
        except ValueError:
            # in this case, get rid of the extension.
            expected_list = [Path(el).stem for el in expected_list]
    expected_list = sorted(expected_list)

    # iterator counting the parsed elements of the init list.
    cnt_init = 0
    # ready to iterate over the expected list and if the respective
    # element of the init_l is missing, copy the previous (or the next
    # if the initia are missing).
    for el_exp in expected_list:
        if cnt_init >= len(init_l):
            # we reached the end of the list, but there are more
            # elements that should be copied.
            # Trick, append a new element to the end, which is greater
            # than al lin the expected list, ensure the rest are copied.
            el1 = int(expected_list[-1]) + 5
            init_l.append(_format_string_name_number(len(init_l[0]), el1))
        if el_exp == init_l[cnt_init]:
            # we have a match, no need to copy anything.
            cnt_init += 1
            continue
        diff = int(el_exp) - int(init_l[cnt_init])
        if diff > 0 and cnt_init < len(init_l) - 1:
            # we need to fast forward the parsing of the second list
            while diff > 0 and cnt_init < len(init_l) - 1:
                cnt_init += 1
                diff = int(el_exp) - int(init_l[cnt_init])
        else:
            # We actually need to copy the previous.
            target = el_exp
            if cnt_init == 0:
                # corner case where the first is missing.
                source = init_l[cnt_init]
            else:
                source = init_l[cnt_init - 1]
            # format the filenames paths for the new (i.e. to be copied) and
            # old (i.e. to copy)files.
            p_src = p + source + suffix
            p_trg = p + target + suffix
            assert (isfile(p_src) and not isfile(p_trg))
            if verbose:
                print('Copying the file {} to the {}.'.format(p_src, p_trg))
            copy2(p_src, p_trg)


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
