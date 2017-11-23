import matplotlib as mpl
mpl.use('Agg')
from os.path import join, isdir, isfile
from functools import partial
import numpy as np
import matplotlib.pyplot as plt
import menpo.io as mio
from menpofit.visualize import view_image_multiple_landmarks
from menpo.image import Image


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


def flip_images(ims, rotate=False):
    """
    Horizontally flips the image(s). For the landmarks with 68 markup it applies
    the menpo convenience function for semantically correcting the flipped ones.
    :param ims: (image or list of images) Menpo images to flip.
    :param rotate: (bool, optional) Add an optional rotation to the image(s).
    :return: The flipped images.
    """
    from menpo.landmark import face_ibug_68_mirrored_to_face_ibug_68 as mirr68
    if not isinstance(ims, list):
        # this is the case of a single image.
        ims = [ims]
    ims_flipped = []
    for im in ims:
        im1 = im.mirror()
        for gr in im1.landmarks.group_labels:
            if im1.landmarks[gr].lms.n_points == 68:
                im1.landmarks[gr] = mirr68(im1.landmarks[gr])
            else:
                m1 = ('The landmark group {} not recognised, '
                      'please correct manually.')
                print(m1.format(gr1))
        if rotate:
            rr = np.random.randint(-20, 20)
            im2 = im1.rotate_ccw_about_centre(rr)
            ims_flipped.append(im2)
        else:
            ims_flipped.append(im1)
    return ims_flipped


# aux function to transform the bb in a [y_min, x_min, y_max, x_max format].
# pts can be of a bounding box/landmark points format.
bb_format_minmax = lambda pts: [np.min(pts[:, 0]), np.min(pts[:, 1]),
                                np.max(pts[:, 0]), np.max(pts[:, 1])]

# aux function to compute the area covered by a bounding box.
# Expects a bounding box in a format of [y_min, x_min, y_max, x_max].
bb_area = lambda bb: (bb[3] - bb[1] + 1) * (bb[2] - bb[0] + 1)


def compute_overlap(pt0, pt1):
    """
    Computes the overlap between two bounding boxes.
    The overlap is defined as:
        area of intersection / area of union
    The bounding boxes (pt0, pt1) are expected in a numpy 2d array
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


def my_2d_rasterizer(im, fn=None, group=None, f=None, crop=False, message=None):
    """
    Visualisation related function. It accepts a menpo image and renders
    a **single** pair of landmarks in a new image.
    The fn offers the chance to apply a custom function to the image.
    ASSUMPTION: There is no check for the case of no landmarks in the image.
    :param im: menpo image.
    :param fn: (optional) If None, then the default .view_landmarks() is
        used for visualisation, otherwise the provided function.
    :param group: (optional) Used in case fn is None.
    :param f: (optional) Matplotlib figure to use. Leave None, unless 
        you know how to modify.
    :param crop: (optional) Crop the resulting visualisation to avoid the
        the excessive white boundary. By default False.
    :param message: (optional) If None, nothing is added in the image. If a
        string is passed, then this is annotated (as text) with matplotlib
        utilities, i.e. the exact same text is written in the image.
    :return: menpo rasterised image.
    """
    if fn is None:
        f = plt.figure(frameon=False)
        if group is None:
            # in this case, assume that the first group of landmarks should suffice.
            group = im.landmarks.group_labels[0]
        r = im.view_landmarks(group=group)
    else:
        fn(im)
    if message is not None:
        assert isinstance(message, str)
        st1 = 25 + 90 * crop
        t = plt.annotate(message, xy=(st1, im.shape[0] - 10), 
                         size=26, fontweight='bold', color='b')
        # set background transparency
        t.set_bbox(dict(color='w', alpha=0.5, edgecolor='w'))
    # get the image from plt
    f.tight_layout(pad=0)
    # Get the pixels directly from the canvas buffer which is fast
    c_buffer, shape = f.canvas.print_to_buffer()
    # Turn buffer into numpy array and reshape to image
    pixels_buffer = np.fromstring(c_buffer,
                                  dtype=np.uint8).reshape(shape[::-1] + (-1,))
    # Prevent matplotlib from rendering
    plt.close(f)
    # Ignore the Alpha channel
    im_plt = Image.init_from_channels_at_back(pixels_buffer[..., :3])
    # ensure that they have the same dtype as the original pixels.
    dtype = im.pixels.dtype
    if dtype != np.uint8:
        if dtype == np.float32 or dtype == np.float64:
            im_plt.pixels = im_plt.pixels.astype(dtype)
            im_plt.pixels = im_plt.pixels / 255.0
        else:
            m1 = 'Not recognised type of original dtype ({}).'
            print(m1.format(dtype))
    if crop:
            # # position to crop the rasterised image (hardcoded for now).
            cri = (50, 60)
            sh1 = im_plt.shape
            im_plt = im_plt.crop((cri[0], cri[1]), (sh1[0] + cri[0], sh1[1] + cri[1]))
    return im_plt


def rasterize_all_lns(im, labels=None, colours='r', marker_sz=5, treat_as_bb=False):
    """
    Visualisation related function. It accepts a menpo image and renders
    all the landmarks that it contains in a new image (effectively
    rasterises all the landmarks in the **same** plot).
    :param im: menpo image.
    :param labels: list or None (optional). If None, then the sorted landmarks
        already attached in the image are used.
    :param colours: list or str (optional). The colours that each landmark group
        obtains in the visualisation. If it is a list, then each group i will be
        aligned with the respective labels[i].
    :param marker_sz: int (optional). The size of the marker for the landmark
        rasterisation.
    :param treat_as_bb: list of bool or bool (optional). Indicates whether each
        should be converted first to bounding box. For every element that is 
        True, then the respective group is visualised as a directed graph
        visualisation. For every False, the default visualisation is
        applied (as points). If simply a bool, the same decision is applied
        for all the groups.
    :return: A new image with all the landmark groups rasterised in a single
        plot/image.
    """
    if labels is None:
        labels = sorted(im.landmarks.group_labels)
    if isinstance(colours, str):
        colours = [colours] * len(labels)
    assert len(colours) >= len(labels)

    if treat_as_bb or isinstance(treat_as_bb, list):
        # a copy is made to avoid distorting the landmark groups.
        im = im.copy()
        # if a single boolean is provided, convert to a list.
        if isinstance(treat_as_bb, bool):
            treat_as_bb = [treat_as_bb] * len(labels)
        for lb, as_bb in zip(labels, treat_as_bb):
            if as_bb:
                im.landmarks[lb] = im.landmarks[lb].lms.bounding_box()

    # visualise all the bounding boxes for the frame.
    c1 = colours[:len(labels)]
    f = plt.figure(frameon=False)
    vis_fn = partial(view_image_multiple_landmarks, groups=labels, subplots_enabled=False,
                     line_colour=c1, marker_face_colour=c1, line_width=5,
                     marker_size=marker_sz, figure_id=f.number,
                     render_legend=False)
    return my_2d_rasterizer(im, fn=vis_fn, f=f)


def check_if_greyscale_values(im, n_sample_points=30, thresh=0.001):
    """
    Check whether a 3-channel image is indeed grayscale.
    Iterates over uniformely sampled points and checks whether the
    values over the channels are the same. The more points are checked the
    better the probability that it is not 'just' a proportion of the image
    black/white.
    :param im:      (menpo image) Image to check.
    :param n_sample_points:  (int) Number of points to check in the image.
    :param thresh:  (float) The threshold for similarity.
    :return: True, if it is indeed greyscale, False otherwise.
    """
    cond = True
    if im.n_channels == 1:
        return True
    for _ in range(n_sample_points):
        # sample random values for row, column check.
        r = np.random.randint(0, im.shape[0])
        c = np.random.randint(0, im.shape[1])
        # # check whether they are (approximately) same
        cond = (np.abs(im.pixels[0, r, c] - im.pixels[1, r, c]) < thresh and
                np.abs(im.pixels[0, r, c] - im.pixels[2, r, c]) < thresh)
        if not cond:
            # Then an element of non grayscale value is found.
            break
    # If the loop is interrupted it has the value wrong.
    return cond
