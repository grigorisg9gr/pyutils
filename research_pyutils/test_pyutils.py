import unittest
import os
from os.path import join, isdir, dirname, realpath, exists
import sys
import glob
import shutil
sep = os.path.sep


def random_string_gen(range1=12):
    import string
    import random
    return ''.join(random.choice(string.ascii_uppercase) for i in range(range1))


class TestImgtovid(unittest.TestCase):
    """
    Tests for checking the basic elementary functions of the imgtovid.py
    call like this:
    a) from terminal:
    python test_pyutils.py
    b) from python shell:
    import unittest, sys; sys.path.append('path');
    from  test_pyutils import TestImgtovid
    suite = unittest.TestLoader().loadTestsFromTestCase(TestImgtovid); unittest.TextTestRunner(verbosity=2).run(suite)

    Copyright (C) 2015 Grigorios G. Chrysos
    available under the terms of the Apache License, Version 2.0

    """

    def setUp(self):
        self.rand_str = random_string_gen()

    def test_unknown_image_type(self):
        try:
            from imgtovid import find_image_type
            find_image_type('.', self.rand_str + '.png44')
        except IOError:
            pass
        except:
            self.assertTrue(False)


    def test_return_image_type(self):
        from imgtovid import find_image_type

        # test that it returns the right type of extension
        self.assertEqual(find_image_type('.', self.rand_str + '.png'), 'png')
        self.assertEqual(find_image_type('.', self.rand_str + '.66554.jpg.jpeg.png'), 'png')  #case with more dots in the filename
        self.assertEqual(find_image_type('.', self.rand_str + '.jpg'), 'jpg')


    import mock
    import imgtovid
    @mock.patch.object(imgtovid, 'create_video', autospec=True)
    def test_search_for_images(self, mock1):
        """
        This test checks the method search_for_images of imgtovid. It requires the mock package to be installed.
        It mocks the call to create_video method to run the tests.
        """

        fnames = list(['0001.png', '0002.png', '0003.png'])
        path_out = self.rand_str
        self.imgtovid.search_for_images(path_out, '.', fnames)
        self.assertTrue(mock1.called)                   # the method should call the create_video

        calls = mock1.mock_calls                        # list of the calls made to the mock of HTTPSession.
        self.assertEqual(len(calls), 1)                 # should be called exactly once

        args1 = calls[0][1]
        dict1 = calls[0][2]
        self.assertEqual(dict1['output_dir'], path_out) # check that the output path is indeed based on the one search_for_images was called with
        self.assertEquals(dict1['image_type'], 'png')   # check image type
        self.assertEqual(args1[1], 4)                      # check the leading zeros, based on fnames above


class Testpyutils(unittest.TestCase):
    def setUp(self):
        self.rand_str = random_string_gen()
        self.files_path = dirname(realpath(__file__)) + sep  # dir of the pyutils files

    def test_count_files_no_path(self):
        """
        Confirm that when count_files (in file_counter.py) is called:
         a) in the pyutils dir, it returns at least two files.
         b) in a non-existent path, it returns negative number of files,
        """
        from file_counter import count_files
        path_in = self.rand_str

        ret = count_files(self.files_path)
        self.assertTrue(ret >= 2)
        # test that all files are more than if just counting directories.
        self.assertTrue(ret >= count_files(self.files_path, directory=True))
        # test that all files in the (sub-)directories are more than those in the current path
        self.assertTrue(ret >= len(os.listdir(self.files_path)))
        if os.path.isdir(path_in):  # if by chance it is a path, continue.
            print('Well, %s is a path in this pc.' % path_in)
            return
        ret = count_files(path_in)
        self.assertTrue(ret <= 0)

    def test_corrupted_file_load_image_in_resize_image(self):
        if 'linux' in sys.platform:
            import subprocess
            subprocess.check_output(['touch ' + '/tmp/00001.png'], shell=True)
            from resize_image import load_image
            im, w, h = load_image('/tmp/', '00001.png', ['png'])
            assert(im == [])


class Test_path_related_functions(unittest.TestCase):
    def setUp(self):
        self.rand_str = random_string_gen()
        self.files_path = dirname(realpath(__file__)) + sep  # dir of the pyutils files
        self.test_mkdir_passed = False
        self.list_files = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt', '00002.txt',
                           '00004.txt', '00002.pt', '00004.pt']

    def _aux_requiring_mkdir(self):
        from auxiliary import whosparent
        from path_related_functions import mkdir_p
        if not self.test_mkdir_passed:
            self.test_mkdir()
        p0 = self.files_path + self.rand_str + sep
        p1 = p0 + 'files' + sep + 'temp' + sep
        if os.path.isdir(p1):
            print('Test of {} is postponed, since the random path exists.'.format(whosparent()))
            return '', ''
        p1 = mkdir_p(p1)
        return p1, p0

    def test_is_path(self):
        from path_related_functions import is_path
        self.assertEqual(isdir(self.files_path), is_path(self.files_path))
        self.assertEqual(isdir('/tmp/'), is_path('/tmp/'))
        p1 = self.files_path + self.rand_str + '/files/'
        if not isdir(p1):
            # http://www.lengrand.fr/2011/12/pythonunittest-assertraises-raises-error/
            self.assertRaises(RuntimeError, lambda: is_path(p1, stop_execution=True))

    def test_mkdir(self):
        """
        Create a path and confirm that the mkdir_p performs as expected:
        a) returns the path, b) the path indeed is created in the os.
        """
        from path_related_functions import mkdir_p
        fold_in = self.rand_str
        if not isdir(self.files_path + fold_in):
            test_p = self.files_path + fold_in + '/pyutils/testing/hello/'
            test_return = mkdir_p(test_p)
            self.assertEqual(test_return, test_p)
            self.assertTrue(isdir(test_p))
            import shutil
            shutil.rmtree(self.files_path + fold_in)
            self.test_mkdir_passed = True
        else:
            print('Test of test_mkdir is postponed, since the random path exists.')

    def test_rename_files(self):
        from path_related_functions import rename_files
        p1, _ = self._aux_requiring_mkdir()
        if not p1:
            return
        for file1 in self.list_files:
            open(p1 + file1, 'a').close()  # http://stackoverflow.com/a/12654798/1716869
        res_bef2 = glob.glob(p1 + '*.txt2')
        self.assertTrue(len(res_bef2) > 0)
        res_bef3 = glob.glob(p1 + '*_2.txt')

        # test no rename cases
        self.assertEqual(rename_files(p1 + self.rand_str, 'txt'), -1)  # non-existent path
        tr = sorted(os.listdir(p1))
        rename_files(p1, self.rand_str)  # non-existent extension of files
        self.assertEqual(tr, sorted(os.listdir(p1)))

        #  rename nr. 1
        self.assertEqual(rename_files(p1, 'txt', '_1', pad_digits=6), 1)
        lres = len(glob.glob(p1 + '*_1.txt'))
        print lres
        self.assertEqual(lres, 0)  # no more _1.txt should exist in the path.
        res2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2)  # .txt2 should be untouched (check different extension).
        res3 = glob.glob(p1 + '*_2.txt')
        self.assertEqual(res_bef3, res3)  # _2.txt should be untouched (check different suffix).
        self.assertTrue(os.path.exists(p1 + '000000.txt'))  # file is actually renamed.

        # rename nr. 2
        self.assertEqual(rename_files(p1,'.txt', new_suffix='9', pad_digits=8), 1)
        lres = len(glob.glob(p1 + '_*.txt'))
        self.assertTrue(lres <= 0)  # no more *.txt should exist in the path.
        res2_2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2_2)  # .txt2 should be untouched (check different extension).
        self.assertTrue(os.path.exists(p1 + '000000009.txt'))  # file is actually renamed (plus new extension added).

        # rename nr. 3
        pt_bef = sorted(glob.glob(p1 + '*.pt'))
        rename_files(p1, '.pt', pad_digits=5, starting_elem=8)
        pt_aft = sorted(glob.glob(p1 + '*.pt'))
        self.assertEqual(len(pt_bef), len(pt_aft))  # number of files should be the same.
        self.assertTrue(pt_bef[0] not in pt_aft)  # files should be renamed.
        pt_final = pt_aft[0][pt_aft[0].rfind('/')+1:]
        self.assertEqual(int(pt_final[:pt_final.rfind('.')]), 8)  # first element should be [0*]8.pt.

        # remove the temp path and files
        shutil.rmtree(self.files_path + self.rand_str)

    def test_change_suffix(self):
        # test similar to the test_rename_files(self).
        from path_related_functions import change_suffix
        p1, _ = self._aux_requiring_mkdir()
        if not p1:     # Skip test if path is not returned.
            return
        for file1 in self.list_files:
            open(p1 + file1, 'a').close()  # http://stackoverflow.com/a/12654798/1716869
        res_bef2 = glob.glob(p1 + '*.txt2')
        self.assertTrue(len(res_bef2) > 0)
        res_bef3 = glob.glob(p1 + '*_2.txt')

        # test no rename cases
        self.assertEqual(change_suffix(p1 + self.rand_str, 'txt'), -1)  # non-existent path
        tr = sorted(os.listdir(p1))
        change_suffix(p1, self.rand_str)  # non-existent extension of files
        self.assertEqual(tr, sorted(os.listdir(p1)))

        self.assertEqual(change_suffix(p1,'.txt', new_suffix='9'), 1)
        lres = len(glob.glob(p1 + '_*.txt'))
        self.assertTrue(lres <= 0)  # no more *.txt should exist in the path.
        res2_2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2_2)  # .txt2 should be untouched (check different extension).

        # remove the temp path and files
        shutil.rmtree(self.files_path + self.rand_str)

    def test_remove_empty_paths(self):
        # test similar to the test_rename_files(self).
        from path_related_functions import (mkdir_p, remove_empty_paths)
        if not self.test_mkdir_passed:
            self.test_mkdir()
        p0 = self.files_path + self.rand_str + sep
        p1 = p0 + 'files' + sep + 'temp' + sep
        if isdir(p1):
            print('Test of test_rename_files is postponed, since the random path exists.')
            return
        p1 = mkdir_p(p1)

        # test that for non existent paths, it prints 'error' message.
        from StringIO import StringIO
        p2 = p1 + 'temp_ia' + sep  # non-existent path
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        remove_empty_paths(p2, verbose=True)
        output = out.getvalue().strip()
        print output
        assert('not exist' in output)
        sys.stdout = saved_stdout

        # test that it actually removes the sub-folders but not the root.
        remove_empty_paths(p0, removeRoot=False, verbose=False)
        assert(not isdir(p1))
        assert(isdir(p0))

        # test that it removes the path including the root.
        p1 = mkdir_p(p1)
        remove_empty_paths(p0, removeRoot=True, verbose=False)
        assert(not isdir(p0))

        # test that it does not remove in case of non-empty folder.
        p1 = mkdir_p(p1)
        open(p1 + 'temp_files.txt', 'a').close()
        remove_empty_paths(p0, removeRoot=True, verbose=False)
        assert(isdir(p1))
        # remove the temp path and files
        shutil.rmtree(p0)

    def test_copy_the_previous_if_missing(self):
        # test similar to the test_rename_files(self).
        from path_related_functions import copy_the_previous_if_missing
        p1, _ = self._aux_requiring_mkdir()
        if not p1:     # Skip test if path is not returned.
            return
        lf = ['001.txt', '003.txt', '009.txt']
        for file1 in lf:
            # http://stackoverflow.com/a/12654798/1716869
            open(p1 + file1, 'a').close()

        # unconstrained call (no init_fr, last_fr)
        copy_the_previous_if_missing(p1)
        assert(os.path.isfile(p1 + '005.txt'))
        os.remove(p1 + '005.txt')

        # constrained start
        copy_the_previous_if_missing(p1, init_fr='006.txt')
        assert(not os.path.isfile(p1 + '005.txt'))

        # constrained end
        copy_the_previous_if_missing(p1, last_fr='004.txt')
        assert(not os.path.isfile(p1 + '005.txt'))

        # TODO: include tests for case of unsimilar names in the
        # same folder, e.g. 001.pts, 001.txt.

        # remove the temp path and files
        shutil.rmtree(self.files_path + self.rand_str)

def test_auxiliary_compare_python_types():
    from auxiliary import compare_python_types
    a = 4
    b = 3
    c, d = compare_python_types(a, b)  # different input
    assert(not c)
    c, d = compare_python_types(a, a)  # same input, should be True
    assert(c)
    c, d = compare_python_types(a, a*1.0)  # different data types
    assert(not c)

    a = [4, 4, 3]
    b = list(a)
    b.append(9)
    c, d = compare_python_types(a, b)  # different size of the lists
    assert(not c)
    b = list(a)
    b[2] = ['grigoris']
    c, d = compare_python_types(a, b)  # different element in the lists
    assert(not c)

    from numpy.random import random
    a1 = random((3, 3))
    c, d = compare_python_types(a1, a1)
    assert(c)
    c, d = compare_python_types(a1, a1 + 10**(-16))
    assert(not c)  # case that they differ a very small number
    c, d = compare_python_types(a1, a1 + 10**(-16), per_elem_numpy=True)
    assert(c)


if __name__ == '__main__':
    import unittest
    from test_pyutils import (TestImgtovid, Testpyutils, Test_path_related_functions)
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestImgtovid)
    unittest.TextTestRunner(verbosity=2).run(suite1)

    suite2 = unittest.TestLoader().loadTestsFromTestCase(Testpyutils)
    unittest.TextTestRunner(verbosity=2).run(suite2)

    suite3 = unittest.TestLoader().loadTestsFromTestCase(Test_path_related_functions)
    unittest.TextTestRunner(verbosity=2).run(suite3)

    test_auxiliary_compare_python_types()
