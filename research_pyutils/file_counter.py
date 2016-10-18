import subprocess
from os.path import isdir


def count_files(path='.', ending='', directory=False):
    """Finds the number of files in the specified path
    Option to specify if only directories should be counted or if a specific ending should be searched."""
    assert isdir(path), 'The initial path is not valid.'
    add_arg = ''
    if directory:
        add_arg = ' -type d '
    p = subprocess.check_output(['find ' + path + add_arg + ' -name "*' + ending + '" -print | wc -l'], shell=True)
    return int(p[:-1])  # ignore the \n in the end


def load_old_results(file_path):
    """Attempts to load most recent results."""
    olddata = {}
    if os.path.isfile(file_path):
        oldfile = open(file_path, 'rb')
        olddata = oldfile.read()
        oldfile.close()
    return olddata


def store_results(file_path, data):
    """Pickles results to compare on next run."""
    output = open(file_path, 'wb')
    output.write(data)
    output.close()


def main(path, filename='tt.txt', save_res=False, ending='', directory=False):
    """
    Find the number of files in the path provided.
    :param path:        The path that we wish to search for files, folders.
    :param filename:    (optional) The filename (with the full path) if we want to compare with previous counting results.
    :param save_res:    (optional) Set to True to save the results in a file (filename variable).
    :param ending:      (optional) If a specific type of files should be searched. By default '' (all files and extensions).
    :param directory:   (optional) Se to True if only the number of sub-directories should be searched.
    :return:            The number of files found, or -1 if it's not a valid path.
    """
    olddata = load_old_results(filename)
    files = count_files(path, ending=ending, directory=directory)
    if olddata != {}: # then there is previous data
        if olddata[:-1].isdigit():
            print(files, int(olddata[:-1]))
    if save_res:
        store_results(filename, files)
    return files

