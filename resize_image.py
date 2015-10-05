# http://stackoverflow.com/a/1048793/1716869
# Resizing images. In case a factor is provided, it rescales to that factor. If only a path is provided,
# then it simply rescales images to have the closest even dimensions.
# The function makes a path walk: From the folder called,it will follow the subfolders and convert all
# images it finds in its path.

import sys
from PIL import Image
from os.path import join, getsize
from os import walk, remove


def load_image(folder, fileName, imgExts):
    ext = fileName[-3:].lower()
    if ext not in imgExts:
        return [], 0, 0
    file_path = join(folder, fileName)
    if getsize(file_path) == 0:  # corrupted image, remove it.
        remove(file_path)
        return [], 0, 0
    im = Image.open(file_path)
    w, h = im.size
    return im, w, h


def resize(folder, fileName, factor=None, imgExts=["png", "bmp", "jpg"], w_base=2, h_base=2):
    im, w, h = load_image(folder, fileName, imgExts)
    if im == []:
        return
    filePath = join(folder, fileName)
    if factor is None:
        # ensure that an image of dimension 640x320 and one of 639x319 will be at the same size after resizing.
        newIm = im.resize((w_base, h_base))
    else:
        newIm = im.resize((int(w*factor), int(h*factor)))
    newIm.save(filePath)


def bulkResize(imageFolder, factor=None):
    imgExts = ["png", "bmp", "jpg"]
    for path, dirs, files in walk(imageFolder):
        if len(files) == 0:
            continue
        _, w, h = load_image(path, files[0], imgExts)  # load the first image, in order to define the shape (h, w)
        w = int((w//2)*2)
        h = int((h//2)*2)
        assert((w % 2 == 0) and (h % 2 == 0))
        try:
            from joblib import Parallel, delayed
            Parallel(n_jobs=-1, verbose=4)(delayed(resize)(path, fileName, factor, imgExts, w, h) for fileName in files)
        except ImportError:
            print('Sequential execution')
            for fileName in files:
                resize(path, fileName, factor, imgExts, w, h)



if __name__ == "__main__":
    imageFolder = sys.argv[1]  # first arg is path to image folder
    if len(sys.argv) > 2:
        resizeFactor = float(sys.argv[2])/100.0  # 2nd is resize in %
    else:
        resizeFactor = None
    bulkResize(imageFolder, resizeFactor)
