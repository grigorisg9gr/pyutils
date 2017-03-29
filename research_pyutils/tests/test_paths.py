from os.path import isdir, isfile, join
from os import listdir, remove
from shutil import rmtree
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from tests_base import (files_path, rand_str, mkdir_msg, test_p,
                        test_p_parent, random_string_gen,
                        aux_require_file_existence)


# # # Tests
def test_mkdir():
    """
    Create a path and confirm that the mkdir_p performs as expected:
    a) returns the path, b) the path indeed is created in the os.
    """
    from research_pyutils import mkdir_p
    if not isdir(files_path + rand_str):
        test_return = mkdir_p(test_p)

        assert test_return == test_p
        assert isdir(test_p)
        # # clean up the files created.
        rmtree(files_path + rand_str)
    else:
        print(mkdir_msg.format('test_mkdir'))


def test_remove_empty_paths_non_existent_path():
    from research_pyutils import mkdir_p, remove_empty_paths

    # test that for non existent paths, it prints 'error' message.
    p2 = join(test_p, 'temp_ia', '')  # non-existent path
    saved_stdout = sys.stdout
    out = StringIO()
    sys.stdout = out
    remove_empty_paths(p2, verbose=True)
    output = out.getvalue().strip()
    # print(output)
    assert('not exist' in output)
    sys.stdout = saved_stdout


def test_remove_empty_paths_basic_tests():
    from research_pyutils import mkdir_p, remove_empty_paths
    p1 = mkdir_p(join(test_p, 'tmp', ''))

    # test that it actually removes the sub-folders but not the root.
    remove_empty_paths(test_p, removeRoot=False, verbose=False)
    assert not isdir(p1)
    assert isdir(test_p)

    # test that it removes the path including the root.
    p1 = mkdir_p(p1)
    remove_empty_paths(test_p, removeRoot=True, verbose=False)
    assert not isdir(test_p)

    # test that it does not remove in case of non-empty folder.
    p1 = mkdir_p(p1)
    open(p1 + 'temp_files.txt', 'a').close()
    remove_empty_paths(test_p, removeRoot=True, verbose=False)
    assert isdir(p1)
    # remove the temp path and files
    rmtree(test_p_parent)


def test_copy_the_previous_if_missing():
    from research_pyutils import copy_the_previous_if_missing, mkdir_p
    mkdir_p(test_p)
    aux_require_file_existence(['001.txt', '003.txt', '009.txt'], test_p)

    # unconstrained call (no init_fr, last_fr)
    copy_the_previous_if_missing(test_p)
    assert isfile(test_p + '005.txt')
    remove(test_p + '005.txt')

    # constrained start
    expected_list = ['006.txt', '007.txt', '008.txt', '009.txt']
    copy_the_previous_if_missing(test_p, expected_list=expected_list)
    print(sorted(listdir(test_p)))
    assert not isfile(test_p + '005.txt')

    # expected list with gaps
    expected_list.remove(expected_list[2])
    remove(test_p + '008.txt')
    copy_the_previous_if_missing(test_p, expected_list=expected_list)
    assert not isfile(test_p + '005.txt')
    assert not isfile(test_p + '008.txt')

    # missing the first few elements.
    expected_list = sorted(listdir(test_p))
    remove(test_p + '001.txt')
    remove(test_p + '002.txt')
    copy_the_previous_if_missing(test_p)
    assert not isfile(test_p + '001.txt')

    # fill the first few elements
    copy_the_previous_if_missing(test_p, expected_list=expected_list)
    assert isfile(test_p + '001.txt')
    assert isfile(test_p + '002.txt')

    # increase the expected ones in the end of the list.
    expected_list.append('012.txt')
    copy_the_previous_if_missing(test_p, expected_list=expected_list)
    assert isfile(test_p + '012.txt')

    # TODO: include tests for case of unsimilar names in the
    # same folder, e.g. 001.pts, 001.txt.

    # remove the temp path and files
    rmtree(test_p_parent)

# # TODO: one test with assertion error for test_count_files_no_path


def test_count_files_basic():
    from research_pyutils import count_files
    n_files = count_files(files_path)
    assert n_files >= 2
    # rough estimate, since it counts the subfolders as well.
    assert n_files == len(listdir(files_path))


def test_count_files_args():
    from research_pyutils import count_files

    n_files = count_files(files_path)
    # ensure that counting only the directories returns less results.
    assert n_files >= count_files(files_path, directory=True)
    # ensure there is at least one python file
    assert count_files(files_path, ending='py') >= 1
    # if counting the subfolder files we will get a greater number.
    n_files_subf = count_files(files_path, subdirs=True)
    assert n_files_subf >= n_files
    tmp_sub = count_files(files_path, ending='py', subdirs=True)
    assert 1 <= count_files(files_path, ending='py') <= tmp_sub

    # no file returned for non-existent extension.
    rand_ext = '.ewrew.rewrew.dfsfds.5056456.k65k6456' + random_string_gen().lower()
    # saved_stdout = sys.stdout
    # out = StringIO()
    # sys.stdout = out
    assert count_files(files_path, ending=rand_ext) == 0
    # sys.stdout = saved_stdout


