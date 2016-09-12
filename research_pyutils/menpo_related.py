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


# aux function to transform the bb in a [y_min, x_min, y_max, x_max format].
# pts can be of a bounding box/landmark points format.
bb_format_minmax = lambda pts : [np.min(pts[:, 0]), np.min(pts[:, 1]), 
                                 np.max(pts[:, 0]), np.max(pts[:, 1])]

# aux function to compute the area covered by a bounding box.
# Expects a bounding box in a format of [y_min, x_min, y_max, x_max].
bb_area = lambda bb : (bb[3] - bb[1] + 1) * (bb[2] - bb[0] + 1)


def compute_overlap(pt0, pt1):
    """
    Computes the overlap between two bounding boxes.
    The overlap is defined as:
        area of intersection / area of union
    The bounding boxes are expected in a numpy 2d array
    e.g. like the lms.points of menpo bounding boxes.
    """

    b0 = bb_format_minmax(pt0)
    b1 = bb_format_minmax(pt1)
    # bounding box of intersection
    bb_i = [max(b0[0], b1[0]), max(b0[1], b1[1]), 
            min(b0[2], b1[2]), min(b0[3], b1[3])]
    
    inter_area = bb_area(bb_i)
    overlap = 0.
    if (bb_i[3] - bb_i[1] + 1 > 0) and inter_area > 0:
        union_area = bb_area(b0) + bb_area(b1) - inter_area
        overlap = inter_area / union_area
        
    return overlap
