import unittest
import os
from os.path import join, isdir, dirname, realpath, exists, isfile
from os import listdir
import sys
import glob
import numpy as np
import shutil

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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
        # case with more dots in the filename
        self.assertEqual(find_image_type('.', self.rand_str + '.66554.jpg.jpeg.png'), 'png')
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
        # check that the output path is indeed based on the one search_for_images was called with
        self.assertEqual(dict1['output_dir'], path_out)
        self.assertEquals(dict1['image_type'], 'png')
        # check the leading zeros, based on fnames above
        self.assertEqual(args1[1], 4)


class Testpyutils(unittest.TestCase):
    def setUp(self):
        self.rand_str = random_string_gen()
        self.files_path = dirname(realpath(__file__)) + sep  # dir of the pyutils files




class Test_path_related_functions(unittest.TestCase):
    def setUp(self):
        self.rand_str = random_string_gen()
        self.files_path = dirname(realpath(__file__)) + sep  # dir of the pyutils files
        self.test_mkdir_passed = False
        self.list_files = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt', '00002.txt',
                           '00004.txt', '00002.pt', '00004.pt']
        self.mkdir_msg = 'Test of {} is postponed, since the random path exists.'

    def _aux_requiring_mkdir(self):
        from auxiliary import whosparent
        from path_related import mkdir_p
        if not self.test_mkdir_passed:
            self.test_mkdir()
        # ATTENTION: The path below should NOT change, otherwise there might be an
        # issue when removing the paths in the testing of the methods.
        p0 = self.files_path + self.rand_str + sep
        p1 = join(p0, 'files', 'temp', '')
        if os.path.isdir(p1):
            print(self.mkdir_msg.format(whosparent()))
            return '', ''
        p1 = mkdir_p(p1)
        return p1, p0

    def test_is_path(self):
        from path_related import is_path
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
        from path_related import mkdir_p
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
            print(self.mkdir_msg.format('test_mkdir'))

    def test_remove_empty_paths(self):
        # test similar to the test_rename_files(self).
        from path_related import (mkdir_p, remove_empty_paths)
        if not self.test_mkdir_passed:
            self.test_mkdir()
        p0 = self.files_path + self.rand_str + sep
        p1 = p0 + 'files' + sep + 'temp' + sep
        if isdir(p1):
            print(self.mkdir_msg.format('test_rename_files'))
            return
        p1 = mkdir_p(p1)

        # test that for non existent paths, it prints 'error' message.
        p2 = p1 + 'temp_ia' + sep  # non-existent path
        saved_stdout = sys.stdout
        out = StringIO()
        sys.stdout = out
        remove_empty_paths(p2, verbose=True)
        output = out.getvalue().strip()
        # print(output)
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
        from path_related import copy_the_previous_if_missing
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
        expected_list = ['006.txt', '007.txt', '008.txt', '009.txt']
        copy_the_previous_if_missing(p1, expected_list=expected_list)
        assert(not os.path.isfile(p1 + '005.txt'))

        # expected list with gaps
        expected_list.remove(expected_list[2])
        os.remove(p1 + '008.txt')
        copy_the_previous_if_missing(p1, expected_list=expected_list)
        assert(not os.path.isfile(p1 + '005.txt'))
        assert(not os.path.isfile(p1 + '008.txt'))

        # missing the first few elements.
        expected_list = sorted(os.listdir(p1))
        os.remove(p1 + '001.txt')
        os.remove(p1 + '002.txt')
        copy_the_previous_if_missing(p1)
        assert(not os.path.isfile(p1 + '001.txt'))

        # fill the first few elements
        copy_the_previous_if_missing(p1, expected_list=expected_list)
        assert(os.path.isfile(p1 + '001.txt'))
        assert(os.path.isfile(p1 + '002.txt'))

        # increase the expected ones in the end of the list.
        expected_list.append('012.txt')
        copy_the_previous_if_missing(p1, expected_list=expected_list)
        # print(sorted(listdir(p1)))
        assert(os.path.isfile(p1 + '012.txt'))

        # TODO: include tests for case of unsimilar names in the
        # same folder, e.g. 001.pts, 001.txt.

        # remove the temp path and files
        shutil.rmtree(self.files_path + self.rand_str)

    def test_count_files_no_path(self):
        """
        Confirm that when count_files is called:
         a) in the pyutils dir, it returns at least two files.
         b) in a non-existent path, it returns negative number of files,
        """
        from path_related import count_files
        path_in = self.rand_str

        ret = count_files(self.files_path)
        self.assertTrue(ret >= 2)
        # test that all files are more than if just counting directories.
        self.assertTrue(ret >= count_files(self.files_path, directory=True))
        # test that all files in the (sub-)directories are more than those in the current path
        self.assertTrue(ret >= len(os.listdir(self.files_path)))


class Test_filenames_changes_functions(unittest.TestCase):
    def setUp(self):
        self.rand_str = random_string_gen()
        self.files_path = dirname(realpath(__file__)) + sep  # dir of the pyutils files
        self.list_files = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt', '00002.txt',
                           '00004.txt', '00002.pt', '00004.pt']

    def _aux_create_path(self):
        # creates a stanrd path in the disk for testing.
        from path_related import mkdir_p
        # ATTENTION: The path below should NOT change, otherwise there might be an
        # issue when removing the paths in the testing of the methods.
        p1 = join(self.files_path, self.rand_str, 'files', 'temp', '')
        if isdir(p1):
            mm = 'Test path of {} exists already, potentially issue in testing.'
            print(mm.format(p1))
        return mkdir_p(p1)

    def test_rename_files(self):
        from filenames_changes import rename_files
        p1 = self._aux_create_path()
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
        print(lres)
        self.assertEqual(lres, 0)  # no more _1.txt should exist in the path.
        res2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2)  # .txt2 should be untouched (check different extension).
        res3 = glob.glob(p1 + '*_2.txt')
        self.assertEqual(res_bef3, res3)  # _2.txt should be untouched (check different suffix).
        self.assertTrue(exists(p1 + '000000.txt'))  # file is actually renamed.

        # rename nr. 2
        self.assertEqual(rename_files(p1,'.txt', new_suffix='9', pad_digits=8), 1)
        lres = len(glob.glob(p1 + '_*.txt'))
        self.assertTrue(lres <= 0)  # no more *.txt should exist in the path.
        res2_2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2_2)  # .txt2 should be untouched (check different extension).
        self.assertTrue(exists(p1 + '000000009.txt'))  # file is actually renamed (plus new extension added).

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
        from filenames_changes import change_suffix
        p1 = self._aux_create_path()

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

    def test_strip_filenames(self):
        # create the path
        p1 = self._aux_create_path()

        lf = ['001@#$%*(&* 00.txt', '003.88.999. 0.txt', '009ASD.tt']
        stripped = ['00100.txt', '003.88.999.0.txt', '009ASD.tt']
        for file1 in lf:
            # http://stackoverflow.com/a/12654798/1716869
            open(p1 + file1, 'a').close()

        from filenames_changes import strip_filenames
        # test 1: convert with an extension
        strip_filenames(p1, ext='.txt')
        assert(isfile(p1 + stripped[0]))
        assert(isfile(p1 + lf[-1]))

        # test: convert all
        strip_filenames(p1)
        for file1 in stripped:
            assert(isfile(p1 + file1))

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


class Test_menpo_related_functions(unittest.TestCase):
    # These tests will fail in case menpo does not exist.
    def init_grigoris(self):
        try:
            import menpo.io as mio
        except ImportError:
            m1 = ('Menpo cannot be imported, so the related tests\n'
                  'might fail.')
            print(m1)

    def test_resize_all_images(self):
        self.init_grigoris()
        import menpo.io as mio
        from menpo_related import resize_all_images
        c = mio.import_builtin_asset
        ims = [c.lenna_png(), c.takeo_ppm(), c.einstein_jpg()]

        cc = resize_all_images(ims)
        m = np.min([im.shape for im in ims], axis=0)
        # check that it is indeed the min
        assert(np.all(cc[0].shape == m))
        # ensure that it's smaller than the original
        assert(np.all(cc[0].shape <= ims[0].shape))

        # apply a different function
        f = lambda sizes: np.median(sizes, axis=0)
        cc1 = resize_all_images(ims, f)
        assert(np.all(cc1[0].shape >= cc[0].shape))
        assert(np.all(cc1[1].shape >= cc[1].shape))

        # apply a fixed size function
        f = lambda sizes: np.array([900, 200])
        cc2 = resize_all_images(ims, f)
        assert(cc2[0].shape[0] == 900)
        assert(cc2[1].shape[1] == 200)

    def test_compute_overlap(self):
        import menpo.io as mio
        from menpo_related import compute_overlap
        # import a builtin landmark file
        ln = mio.import_builtin_asset.lenna_ljson()

        # convert it first to a bounding box:
        bb0 = ln.lms.bounding_box()
        # first test with same overlap.
        ov1 = compute_overlap(bb0.points, bb0.points)
        assert np.allclose(ov1, 1.)
        # test now the bb vs the ln points
        ov2 = compute_overlap(bb0.points, ln.lms.points)
        assert np.allclose(ov2, 1.)

        bb1 = bb0.points - 400
        ov3 = compute_overlap(bb0.points, bb1)
        assert np.allclose(ov3, 0.)

    def test_flip_images(self):
        self.init_grigoris()
        import menpo.io as mio
        from menpo_related import flip_images

        im = mio.import_builtin_asset.breakingbad_jpg()
        ims = flip_images(im)
        assert len(ims) == 1
        # get the pure mirror.
        mirror = im.mirror()
        assert np.allclose(ims[0].pixels, mirror.pixels)
        # ensure that the landmarks are 'semantically correct':
        # a) not the same as the original.
        gr = im.landmarks.group_labels[0]
        lms = ims[0].landmarks[gr].lms
        assert not np.allclose(lms.points, im.landmarks[gr].lms.points)
        # b) not close with the pure mirror.
        assert not np.allclose(lms.points, mirror.landmarks[gr].lms.points)
        # c) by reversing the flip, we should end up in the same.
        ims2 = flip_images(ims)
        lms = ims2[0].landmarks[gr].lms
        assert np.allclose(lms.points, im.landmarks[gr].lms.points)
        # TODO: ideally here more tests that check random points, e.g. the
        # transformation of point 0 in the flipped. Also, more cases.

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

    suite4 = unittest.TestLoader().loadTestsFromTestCase(Test_menpo_related_functions)
    unittest.TextTestRunner(verbosity=2).run(suite4)

    suite5 = unittest.TestLoader().loadTestsFromTestCase(Test_filenames_changes_functions)
    unittest.TextTestRunner(verbosity=2).run(suite5)
