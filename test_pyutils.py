import unittest


def random_string_gen(range1=12):
    import string
    import random
    return ''.join(random.choice(string.ascii_uppercase) for i in range(range1))


class TestImgtovid(unittest.TestCase):
    """
    Tests for checking the basic elementary functions of the imgtovid.py
    call like this:
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


