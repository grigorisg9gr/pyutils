import matplotlib as mpl
mpl.use('Agg')
from os.path import join, isdir, isfile
from functools import partial
import matplotlib.pyplot as plt
from menpofit.visualize import view_image_multiple_landmarks


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
            im_plt.pixels /= 255.0
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