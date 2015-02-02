# http://stackoverflow.com/a/1048793/1716869
# Resizing images. In case a factor is provided, it rescales to that factor. If only a path is provided,
# then it simply rescales images to have the closest even dimensions.
# The function makes a path walk, so from the folder calle,it will follow the subfolders and convert all
# images it finds in its path.

import sys

def resize(folder, fileName, factor=None):
    from PIL import Image
    import sys, os
    filePath = os.path.join(folder, fileName)
    im = Image.open(filePath)
    w, h  = im.size
    if factor == None:
        newIm = im.resize((int((w/2)*2), int((h/2)*2)))
    else:
        newIm = im.resize((int(w*factor), int(h*factor)))
    newIm.save(filePath)


def bulkResize(imageFolder, factor=None):
    import sys, os
    imgExts = ["png", "bmp", "jpg"]
    for path, dirs, files in os.walk(imageFolder):
        for fileName in files:
            ext = fileName[-3:].lower()
            if ext not in imgExts:
                continue

            resize(path, fileName, factor)


if __name__ == "__main__":
    imageFolder = sys.argv[1] # first arg is path to image folder
    if len(sys.argv) > 2:
        resizeFactor=float(sys.argv[2])/100.0# 2nd is resize in %
    else:
        resizeFactor = None
    bulkResize(imageFolder, resizeFactor)
