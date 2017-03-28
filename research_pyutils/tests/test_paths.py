from os.path import isdir, dirname, realpath, isfile, join
from os import listdir
from shutil import rmtree


def random_string_gen(range1=12):
    import string
    import random
    return ''.join(random.choice(string.ascii_uppercase) for i in range(range1))

# # setup variables and functions
rand_str = random_string_gen()
files_path = join(dirname(realpath(__file__)), '')
list_files = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt', '00002.txt',
              '00004.txt', '00002.pt', '00004.pt']
mkdir_msg = 'Test of {} is postponed, since the random path exists.'


# # # Tests

def test_mkdir():
    """
    Create a path and confirm that the mkdir_p performs as expected:
    a) returns the path, b) the path indeed is created in the os.
    """
    from research_pyutils import mkdir_p
    if not isdir(files_path + rand_str):
        test_p = join(files_path, rand_str, 'testing', 'mkdirperfr', '')
        test_return = mkdir_p(test_p)

        assert test_return == test_p
        assert isdir(test_p)
        # # clean up the files created.
        rmtree(files_path + rand_str)
    else:
        print(mkdir_msg.format('test_mkdir'))