from os.path import isdir, isfile, join
from os import listdir, remove
from shutil import rmtree
from glob import glob

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from tests_base import (files_path, rand_str, mkdir_msg, test_p,
                        test_p_parent, random_string_gen,
                        aux_require_file_existence)

filenames = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt',
             '00002.txt', '00004.txt', '00002.pt', '00004.pt']


def test_rename_files_basic():
    """
    Using a new path, ensure that the basic call to rename_files returns
    the expected results.
    """
    from research_pyutils import rename_files, mkdir_p
    mkdir_p(test_p)
    aux_require_file_existence(filenames, test_p)

    # non-existent path case
    assert rename_files(test_p + rand_str, 'txt') == -1
    # non-existent extension
    assert rename_files(test_p + rand_str, 'txt_' + rand_str) == -1

    # simple rename case
    if len(glob(test_p + '*_1.txt')) > 0:
        res_bef2 = glob(test_p + '*.txt2')
        assert rename_files(test_p, 'txt', '_1') == 1
        # no more _1.txt should exist in the path.
        assert len(glob(test_p + '*_1.txt')) == 0
        # meanwhile, the rest should be untouched,
        res2 = glob(test_p + '*.txt2')
        assert res2 == res_bef2 and len(res2) > 0
    else:
        raise RuntimeError('why does this exist?')

    rmtree(test_p_parent)


def test_rename_files_more():
    """
    Additional tests for rename_files() for optional arguments.
    """
    from research_pyutils import rename_files, mkdir_p
    from pathlib import Path
    mkdir_p(test_p)
    aux_require_file_existence(filenames, test_p)

    res_bef2 = glob(test_p + '*_2.txt')
    assert len(res_bef2) > 0

    # # # rename case with padding
    assert rename_files(test_p, 'txt', '_1', pad_digits=6) == 1
    res2 = glob(test_p + '*_2.txt')
    assert res2 == res_bef2
    assert isfile('{}{:06}.txt'.format(test_p, 0))

    # # # rename case with new suffix
    assert rename_files(test_p, 'txt', new_suffix='9', pad_digits=8) == 1
    # no more *.txt should exist in the path.
    assert len(glob(test_p + '_*.txt')) == 0
    # file is actually renamed (plus new extension added)
    assert isfile('{}{:09d}.txt'.format(test_p, 9))

    # # # rename case with different start
    pt_bef = sorted(glob(test_p + '*.pt'))
    rename_files(test_p, '.pt', pad_digits=5, starting_elem=8)
    # number of files should be the same.
    pt_aft = sorted(glob(test_p + '*.pt'))
    assert len(pt_bef) == len(pt_aft)
    # files should be renamed.
    assert pt_bef[0] not in pt_aft
    # first element should be [0*]8.pt.
    assert int(Path(pt_aft[0]).stem) == 8

    rmtree(test_p_parent)



