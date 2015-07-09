import unittest
import os

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
        self.imgtovid.search_for_images(path_out,'.',fnames)
        self.assertTrue(mock1.called)                   # the method should call the create_video

        calls = mock1.mock_calls                        # list of the calls made to the mock of HTTPSession.
        self.assertEqual(len(calls), 1)                 # should be called exactly once

        args1 = calls[0][1]; dict1 = calls[0][2]
        self.assertEqual(dict1['output_dir'], path_out) # check that the output path is indeed based on the one search_for_images was called with
        self.assertEquals(dict1['image_type'], 'png')   # check image type
        self.assertEqual(args1[1], 4)                      # check the leading zeros, based on fnames above


class Testpyutils(unittest.TestCase):
    def setUp(self):
        self.rand_str = random_string_gen()
        self.files_path = os.path.dirname(os.path.realpath(__file__)) + '/'  # dir of the pyutils files
        self.test_mkdir_passed = False
        self.list_files = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt', '00002.txt',
                           '00004.txt', '00002.pt', '00004.pt']

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
        if os.path.isdir(path_in):  # if by chance it is a path, continue.
            print('Well, %s is a path in this pc.' % path_in)
            return
        ret = count_files(path_in)
        self.assertTrue(ret <= 0)

    def test_mkdir(self):
        """
        Create a path and confirm that the mkdir_p performs as expected:
        a) returns the path, b) the path indeed is created in the os.
        """
        from path_related_functions import mkdir_p
        fold_in = self.rand_str
        if not os.path.isdir(self.files_path + fold_in):
            test_p = self.files_path + fold_in + '/pyutils/testing/hello/'
            test_return = mkdir_p(test_p)
            self.assertEqual(test_return, test_p)
            self.assertTrue(os.path.isdir(test_p))
            import shutil
            shutil.rmtree(self.files_path + fold_in)
            self.test_mkdir_passed = True
        else:
            print('Test of test_mkdir is postponed, since the random path exists.')

    def test_rename_files(self):
        from path_related_functions import (rename_files, mkdir_p)
        import glob, shutil
        if not self.test_mkdir_passed:
            self.test_mkdir()
        p1 = self.files_path + self.rand_str + '/files/'
        if os.path.isdir(p1):
            print('Test of test_rename_files is postponed, since the random path exists.')
            return
        p1 = mkdir_p(p1)
        for file1 in self.list_files:
            open(p1 + file1, 'a').close()  # http://stackoverflow.com/a/12654798/1716869
        res_bef2 = glob.glob(p1 + '*.txt2')
        self.assertTrue(len(res_bef2) > 0)
        res_bef3 = glob.glob(p1 + '*_2.txt')

        ## rename nr. 1
        self.assertEqual(rename_files(p1, 'txt', '_1', pad_digits=6), 1)
        lres = len(glob.glob(p1 + '*_1.txt'))
        print lres
        self.assertEqual(lres, 0)  # no more _1.txt should exist in the path.
        res2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2)  # .txt2 should be untouched (check different extension).
        res3 = glob.glob(p1 + '*_2.txt')
        self.assertEqual(res_bef3, res3)  # _2.txt should be untouched (check different suffix).
        self.assertTrue(os.path.exists(p1 + '000000.txt'))  # file is actually renamed.

        ## rename nr. 2
        self.assertEqual(rename_files(p1,'txt', new_suffix='9', pad_digits=8), 1)
        lres = len(glob.glob(p1 + '_*.txt'))
        self.assertTrue(lres <= 0)  # no more *.txt should exist in the path.
        res2_2 = glob.glob(p1 + '*.txt2')
        self.assertEqual(res_bef2, res2_2)  # .txt2 should be untouched (check different extension).
        self.assertTrue(os.path.exists(p1 + '000000009.txt'))  # file is actually renamed (plus new extension added).

        # remove the temp path and files
        shutil.rmtree(self.files_path + self.rand_str)




if __name__ == '__main__':
    import unittest
    from test_pyutils import (TestImgtovid, Testpyutils)
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestImgtovid)
    unittest.TextTestRunner(verbosity=2).run(suite1)

    suite2 = unittest.TestLoader().loadTestsFromTestCase(Testpyutils)
    unittest.TextTestRunner(verbosity=2).run(suite2)
