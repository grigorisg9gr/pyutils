# http://stackoverflow.com/a/1048793/1716869
# Resizing images. In case a factor is provided, it rescales to that factor. If only a path is provided,
# then it simply rescales images to have the closest even dimensions.
# The function makes a path walk, so from the folder calle,it will follow the subfolders and convert all
# images it finds in its path.

import sys
from PIL import Image
import os

def load_image(folder, fileName, imgExts):
    ext = fileName[-3:].lower()
    if ext not in imgExts:
        return
    filePath = os.path.join(folder, fileName)
    im = Image.open(filePath)
    w, h = im.size
    return im, w, h

def resize(folder, fileName, factor=None, imgExts=["png", "bmp", "jpg"], w_base=2, h_base=2):
    im, w, h = load_image(folder, fileName, imgExts)
    filePath = os.path.join(folder, fileName)
    if factor is None:
        # ensure that an image of dimension 640x320 and one of 639x319 will be at the same size after resizing.
        newIm = im.resize((w_base, h_base))
    else:
        newIm = im.resize((int(w*factor), int(h*factor)))
    newIm.save(filePath)


def bulkResize(imageFolder, factor=None):
    imgExts = ["png", "bmp", "jpg"]
    for path, dirs, files in os.walk(imageFolder):
        if len(files) == 0:
            continue
        _, w, h = load_image(path, files[0], imgExts)  # load the first image, in order to define the shape (h, w)
        w = int((w/2)*2)
        h = int((h/2)*2)
        try:
            from joblib import Parallel, delayed
            Parallel(n_jobs=-1, verbose=4)(delayed(resize)(path, fileName, factor, imgExts, w, h) for fileName in files)
        except ImportError:
            print('Sequential execution')
            for fileName in files:
                resize(path, fileName, factor, imgExts, w, h)



if __name__ == "__main__":
    imageFolder = sys.argv[1] # first arg is path to image folder
    if len(sys.argv) > 2:
        resizeFactor = float(sys.argv[2])/100.0 # 2nd is resize in %
    else:
        resizeFactor = None
    bulkResize(imageFolder, resizeFactor)
