from os.path import join, isdir, isfile
import numpy as np
import menpo.io as mio


def process_lns_path(process, shapes=None, p_in=None, p_out=None, overwrite=None):
    """
    Processes a list of landmark files. The processing is performed per shape (file)
    and depends on the process function defined.
    Can be provided either the shapes directly or an import path.
    If an exporting path is provided, the bounding boxes will be
    exported there.

    :param process: (function) Process function that accepts a landmark (menpo.landmark)
                    and returns the same type processed.
    :param shapes:  (list, optional) List of shapes.
    :param p_in:    (string, optional) Input path for shapes if shapes is not provided.
    :param p_out:   (string, optional) Output path for the processed landmarks.
    :param overwrite: (bool, optional) Whether to overwrite existing files in p_out.
    :return:
    """
    if p_out is not None:
        assert(isdir(p_out))

    if shapes is None:
        # import the shapes from p_in.
        assert(isdir(p_in))
        shapes = list(mio.import_landmark_files(p_in))

    ln_out = []
    # dummy image
    im = mio.import_builtin_asset.lenna_png()
    # loop over the shapes to convert to bounding boxes.
    for ln in shapes:
        # process each shape by utilising the process function.
        im.landmarks['g'] = process(ln)

        if p_out is not None:
            # if path is provided, export it.
            mio.export_landmark_file(im.landmarks['g'], p_out + ln.path.name, 
                                     overwrite=overwrite)
        ln_out.append(im.landmarks['g'])
        
    return ln_out


def from_ln_to_bb_path(shapes=None, p_in=None, p_out=None, overwrite=None):
    """
    Wrapper around process_lns_path() for converting the landmarks to the
    respective tightest bounding boxes.
    Calls the menpo convenience method of bounding_box() for the landmarks.
    :param shapes:  (list, optional) List of shapes.
    :param p_in:    (string, optional) Input path for shapes if shapes is not provided.
    :param p_out:   (string, optional) Output path for the processed landmarks.
    :param overwrite: (bool, optional) Whether to overwrite existing files in p_out.
    :return:
    """
    f = lambda ln: ln.lms.bounding_box()
    return process_lns_path(f, shapes, p_in, p_out, overwrite)


def resize_all_images(images, f=None):
    """
    Resizes all images to a new size, defined by the function f.
    :param images: (list) Menpo images.
    :param f: (function, optional) If not provided, np.min is considered as the
        default function. If provided, it should accept a 2d array with all the
        shapes and return the final shape (2-element numpy vector).
    :return: (list) Resized menpo images.
    """
    if f is None:
        f = lambda sizes: np.min(sizes, axis=0)
    sizes = np.array([im.shape for im in images])
    # define the new size based on f
    final_size = f(sizes)
    # resize the images to the final size
    images_resized = [im.resize(final_size) for im in images]
    return images_resized
