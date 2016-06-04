import re
from shutil import move
from glob import glob
from os.path import sep, isdir, isfile, join
from os import rename


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
    list2rename = sorted(glob(file_path + '*' + initial_suffix + ext))
    for cnt, elem_p in enumerate(list2rename):
        rename(elem_p, file_path + padding % (cnt + starting_elem) + new_suffix + ext)
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
    list2rename = sorted(glob(file_path + '*' + end1))
    for cnt, elem_p in enumerate(list2rename):
        elem_n = elem_p[elem_p.rfind('/') + 1:]
        till_pos = -end_p if elem_n.rfind('_') < 0 else elem_n.rfind('_')
        rename(elem_p, file_path + elem_n[:till_pos] + new_suffix + ext)
    return 1


def strip_filenames(path, ext=''):
    """
    Strips the filenames from whitespaces and other 'problematic' chars.
    In other words converts the filenames to alpharethmetic chars.
    :param path:    (String) Base path for the filenames.
    :param ext:     (String, optional) If provided, the glob will rename only these files.
    :return:
    """

    pattern = re.compile('[^a-zA-Z0-9.]+')
    for cl in sorted(glob(path + '*' + ext)):
        # get only the filename
        cl1 = cl[cl.rfind(sep) :]
        # strip all white spaces, quatation points, etc.
        name = pattern.sub('', cl1)
        move(path + cl1, path + name)