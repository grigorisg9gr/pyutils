import re
from shutil import move
from glob import glob
from os.path import sep


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