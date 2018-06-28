from os.path import join, isdir, isfile
from functools import partial
import numpy as np
import menpo.io as mio
from menpo.image import Image
from menpo.shape import PointCloud


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
    :return: The flipped images. If the images contain landmarks of ibug68 format,
        those will also be flipped appropriately (semantically).
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


def pad_img(im, sht, force_shape=True):
    """
    Pad an image to a given shape. If the image is bigger than the  target shape (sht),
    then depending on the force_shape an action is decided.
    Warning: experimental function, not tested for all cases!
    :param im: Menpo type image.
    :param sht: (typle, list, nd.array) Target shape for the image.
    :param force_shape: (bool, opt) If True, then the shape is forced to be reduced to the target
        one if bigger than that.
    :return: The new image reshaped in the target shape (unless force_shape == False).
    """
    # TODO: improve this function for all cases.
    # # lambda function as 'macro' for avoiding a long pad below:
    padl = lambda px, pdd1=(0, 0), pdd2=(0, 0): np.pad(px, ((0, 0), pdd1, pdd2), mode='constant')
    px = im.pixels
    sh = np.array(sht) - np.array(im.shape)
    if sh[0] < 0:
        if force_shape:
            px = px[:, -sh[0]:, :]
        else:
            print('The image is larger than the target shape.')
            return im
    if sh[1] < 0:
        return Image(px, copy=False).resize(sht)
    if sh[0] > 0:
        px = padl(px, pdd1=(sh[0] // 2, sh[0] // 2 + sh[0] % 2))
    if sh[1] > 0:
        # # TEMP, fix this one.
        px = padl(px, pdd2=(sh[1] // 2, sh[1] // 2 + sh[1] % 2))
    return Image(px, copy=False)


def pad_with_same_aspect_ratio(im, shtarget1, max_rescale=2., return_info=False):
    """
    Pads an image based on the max of the original dimensions. Also,
    if the rescale is bigger than max_recale, it performs a rescale up
    to this point and the rest is padded.
    The goal is to result in an image with similar aspect ratio as the
    original image.
    Warning: experimental function, not tested for all cases!
    :param im:  Menpo type image.
    :param shtarget1:  (list, tuple, nd.array) Target shape for the image.
    :param max_rescale: (float, optional) Maximum rescale allowed for the image.
    :param return_info: (bool, optional) If True, it returns the rescaling and the
           padding done (e.g. in case we want to reverse it).
    :return: The padded/rescale image.
    """
    #  TODO: think better all the cases, (e.g. max_rescale < 1). -> It works.
    resc = min(max_rescale, np.max(shtarget1) / np.max(im.shape))
    im1 = im.rescale(resc)
    # # sh is effectively the padding conducted in the image, computed here only for
    # # the case that we want to return the info
    sh = np.array(shtarget1) - np.array(im1.shape)
    im1 = pad_img(im1, shtarget1)
    if return_info:
        return im1, resc, sh
    return im1


def get_segment_image(im, n_segment, n_total, axis=1):
    """
    Returns the segment of the image requested. This is the reverse of
    concatenate, i.e. given a (concatenated) image, it divides it into
    'n_total' segments and returns the 'n_segment'.
    :param im: Menpo type image (channels in front).
    :param n_segment: (int) The segment to return, 1-based.
    :param n_total: (int) Total number of segments to divide the image.
    :param axis: (int)
    :return: Segment of the image (menpo image type).
    """
    sh1 = im.pixels.shape[axis] // n_total
    if im.pixels.shape[axis] % n_total != 0:
        print('Not exact division into segments.')
    if axis == 1:
        px = im.pixels[:, (n_segment - 1) * sh1: n_segment * sh1, :]
    elif axis == 2:
        px = im.pixels[:, :, (n_segment - 1) * sh1: n_segment * sh1]
    else:
        px = im.pixels[(n_segment - 1) * sh1: n_segment * sh1]
    return Image(px)


def _info_from_first_line(line):
    """
    Gets the info from the first line of landmarks' txt. The format of the file
    is hardcoded for now, e.g. the expected numbers and fields.
    It returns a dictionary, which enables future extensions of what is returned.

    Along with the functions _from_line_to_vec, from_txt_to_numpy_points, and
    access_ln_frame they are the functions to access the single txt (with sparse
    landmarks) per video.
    Unless you know how to call the function, please avoid calling it directly, it is used
    internally by the from_txt_to_numpy_points().
    :param line:
    :return: Dict with meta-data.
    """
    info = {}
    # # get the framename of the first (assumed int!)
    info['init_framename'] = int(line[line.find(':') + 1: line.find('\t')])
    # # get the number of frames.
    line1 = line[line.find('n_frames:'):]
    info['n_frames'] = int(line1[9: line1.find('\t')])
    # # get the number of landmarks.
    line2 = line[line.find('n_landmarks:'):]
    info['n_landm'] = int(line2[12: line2.find('\n')])
    return info


def _from_line_to_vec(line, vec_sz):
    """
    Accepts a line from a txt (str) and converts it into a numpy vector.
    Unless you know how to call the function, please avoid calling it directly, it is used
    internally by the from_txt_to_numpy_points().

    :param line: (str) A string that contains numbers separated by commas.
    :param vec_sz: (int) Number of numbers expected in the line.
    :return: Numpy vector with the numbers.
    """
    # # out of the line, get only the 'vector' (string formatted).
    line_vec = line[line.find('\t') + 1:]
    # # convert the string into a numpy vector and return it.
    # # The separator is hardcoded based on the export code.
    return np.fromstring(line_vec, sep=', ', count=vec_sz)


def from_txt_to_numpy_points(pln_txt):
    """
    Converts the txt file (the path of which is provided) to a numpy
    matrix containing numbers (e.g. landmark points).

    After the txt is wrapped, it calls external functions for parsing both
    the meta-data and the actual numbers. Those functions have hardcoded
    assumptions regarding the txt format, e.g.
    the first frame info, the format of every line.
    :param pln_txt: (str) Path of the txt file to be parsed.
    :return: i) the numpy matrix with the points, ii) a dict with the
        meta-data info, iii) positions that it found valid points (which might
        not be sequential).
    """
    txt = open(pln_txt, 'rt')
    lines = txt.readlines()
    info = _info_from_first_line(lines[0])
    # # get the size of the vectorized landmark points.
    vec_sz = info['n_landm'] * 2

    # # points_np: Will have all the landmarks for the clip if those exist. If
    # # a landmark does not exist, then the element will consist of zeros.
    # # converted to numpy float32 to avoid excessive use of memory (sub-pixel coordinates).
    points_np = np.zeros((info['n_frames'], info['n_landm'], 2), dtype=np.float32)

    # # positions_found: The positions (relative to the first frame) that we
    # # found landmarks on.
    positions_found = []

    # # Iterate over all the lines and export the points in the points_np.
    # # The iterator starts from -1, in order to ignore the first dummy row.
    for cnt, line in enumerate(lines):
        if cnt == 0:
            continue
        pt = _from_line_to_vec(line, vec_sz)
        # # get the actual number of frame that these points correspond to.
        cnt1 = int(line[:line.find('::')])
        # # assign the point after reshaped to the appropriate position (row declares
        # # the ascending number of the frame).
        points_np[cnt1] = pt.reshape((-1, 2))
        positions_found.append(cnt1)
    return points_np, info, positions_found


def access_ln_frame(points, info_txt, idx=None, frame_name=None,
                    allow_fail=True, eps=1e-4):
    """
    Given a numpy 3D matrix (e.g. landmark points for the whole clip),
    the index OR the frame name, it returns the landmarks for the
    particular frame.
    In other words, it allows the direct access to a particular frames'
    numbers (landmarks).

    :param points: (numpy matrix) The matrix that contains the data.
    :param info_txt: (dict) Dictionary with meta-data.
    :param idx:  (int, optional) If we want a particular index of the data,
        we provide it with idx.
    :param frame_name: (str, optional) Either provide this or the idx to
        find a particular frame.
    :param allow_fail: (bool, optional) If True, if the landmark does not exist, we
        catch the error and return None, otherwise there will be an error
        if it does not exist.
    :param eps: (float, optional) Accuracy to ensure that the landmark
        does not include zeros (considered dummy).
    :return: The PointCloud with the landmarks (or None if not found).
    """
    if idx is None:
        # # In this case, the name should have been provided, so convert
        # # this to an index. Assumption: Based on assumptions during
        # # exporting, the frame_name is the stem that contains *only*
        # # numbers. Also, same padding as init_framename assumed.
        idx = int(frame_name) - info_txt['init_framename']
    if allow_fail:
        try:
            pt = points[idx]
        except:
            return None
    else:
        pt = points[idx]
    if pt[0, 0] < eps and pt[0, 1] < eps:
        # # check whether all landmarks are almost zero.
        if np.all(np.abs(pt) < eps):
            # # If the landmarks are zero, return none.
            return None
    return PointCloud(pt)


