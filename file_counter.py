import subprocess
import os

def count_files(path='.', ending='', directory=False):
    """Finds the number of files in the specified path
    Option to specify if only directories should be counted or if a specific ending should be searched."""
    if not os.path.isdir(path):
        print('The path is not valid.')
        return -1
    if not directory:
        p = subprocess.check_output(['find ' + path + ' -name "*' + ending + '" -print | wc -l'], shell=True)
    else:
        p = subprocess.check_output(['find ' + path + ' -type d -name "*' + ending + '" -print | wc -l'], shell=True)
    return p[:-1] # ignore the \n in the end


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
    olddata = load_old_results(filename)
    files = count_files(path, ending=ending, directory=directory)
    if olddata != {}: # then there is previous data
        if olddata[:-1].isdigit():
            print files, int(olddata[:-1])
    if save_res:
        store_results(filename, files)
    return files

