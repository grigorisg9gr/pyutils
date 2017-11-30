from os.path import isdir, dirname, realpath, join

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def random_string_gen(range1=12):
    import string
    import random
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(range1))

# # setup variables and functions
rand_str = random_string_gen()
files_path = join(dirname(realpath(__file__)), '')
list_files = ['00001.txt', '00001_1.txt', '00002_1.txt2', '00002_2.txt', '00002.txt',
              '00004.txt', '00002.pt', '00004.pt']
mkdir_msg = 'Test of {} is postponed, since the random path exists.'
# format a set-up path (attention, the parent path(s) of this might be hardcoded).
test_p_parent = join(files_path, 'test_mkdirs', rand_str, '')
if isdir(test_p_parent):
    print(mkdir_msg.format('tests_general_testing_path'))
else:
    rand_str = random_string_gen(range1=22)
    test_p_parent = join(files_path, rand_str, '')
test_p = join(test_p_parent, 'testing', 'files', '')


def aux_require_file_existence(filenames, path):
    # Aux function: creates iteratively the files requested in the path.
    if not isdir(path):
        assert isdir(path)  # # temp for debugging.
        return
    for file1 in filenames:
        # http://stackoverflow.com/a/12654798/1716869
        open(path + file1, 'a').close()

# # grigoris, this file contains few common functions, reference variables that
# # are required in all the files.