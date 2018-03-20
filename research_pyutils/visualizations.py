import matplotlib as mpl
mpl.use('Agg')
from os.path import join, isdir, isfile, sep
from os import system
import numpy as np
from functools import partial
from pathlib import Path
import matplotlib.pyplot as plt
import menpo.io as mio
from menpo.image import Image
from menpofit.visualize import view_image_multiple_landmarks

from .path_related import mkdir_p
try:
    from .personal import list_to_latex
except ImportError:
    m = ('Unfortunately, you cannot use the function '
         'plot_image_latex_with_subcaptions().')
    print(m)


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


def plot_image_latex_with_subcaptions(folds, pb, pout, name_im, legend_names=None,
                                      normalise=None, allow_fail=False,
                                      overwr=True):
    """
    Customised function for my papers. It plots variations of an image (i.e. different
        images) next to each other with the respective legend names.
    The idea is: Import one by one from the folds, normalise (e.g. resize) and export each
        with a predictable name. Write the tex file and compile it to create the image
        with the several subplots and the custom labels.
    Attention: Because of latex compilation, this function writes and reads from the disk,
        so pay attention to the pout path.
    :param folds: (list) Names of the parent folders to search the image to. The assumption
        is that all those are relative to pb path.
    :param pb:    (str) Base path where the images to be imported exist.
    :param pout:  (str) Path to export the result in. The method will write the result in a
        new sub-folder named 'concatenated'.
    :param name_im: (str) Name (stem + suffix) of the image to be imported from folds.
    :param legend_names: (optional, list or None) If provided, it should match in length the
        folds; each one will be respectively provided as a sub-caption to the respective image.
    :param normalise: (optional, function or None) If not None, then the function accepts
        a menpo image and normalises it.
    :param allow_fail: (optional, list or bool) If bool, it is converted into a list of
        length(folds). The images from folds that do not exist
        will be ignored if allow_fail is True.
    :param overwr:     (optional, bool) To overwrite or not the intermediate results written.
    :return:
    # TODO: extend the formulation to provide freedom in the number of elements per line etc.
    """
    # # short lambda for avoiding the long import command.
    import_im = lambda p, norm=False: mio.import_image(p, landmark_resolver=None,
                                                       normalize=norm)
    # # names_imout: Names of the output images in the disk.
    # # names_meth: Method of the name to put in the sub-caption.
    names_imout, names_meth = [], []
    # # if allow_fail is provided as a single boolean, convert into a list, i.e.
    # # each one of the folders has different permissions.
    if not isinstance(allow_fail, list):
        allow_fail = [allow_fail for _ in range(len(folds))]

    for cnt, fold in enumerate(folds):
        if allow_fail[cnt]:
            # # In this case, we don't mind if an image fails.
            try:
                im = import_im(join(pb, fold, name_im))
            except:
                continue
        else:
            im = import_im(join(pb, fold, name_im))
        # # get the name for the sub-caption (legend).
        if legend_names is not None:
            names_meth.append(legend_names[cnt])
        else:
            assert 0, 'Not implemented for now! Need to use map_to_name()'
        # # Optionally resize the image.
        if normalise:
            im = normalise(im)
        # # export the image into the disk and append the name exported in the list.
        nn = '{}_{}'.format(Path(fold).stem, im.path.name)
        mio.export_image(im, pout + nn, overwrite=overwr)
        names_imout.append(nn)

    # # export into a file the latex command.
    nlat = Path(name_im).stem
    fo = open(pout + '{}.tex'.format(nlat),'wt')
    fo.writelines(('\\documentclass{article}\\usepackage{amsmath}'
                   '\n\\usepackage{graphicx}\\usepackage{subfig}'
                   '\\begin{document}\n'))
    list_to_latex(names_imout, wrap_subfloat=True, names_subfl=names_meth, pbl='',
                  file_to_print=fo, caption='')
    fo.writelines('\\thispagestyle{empty}\\end{document}\n')
    fo.close()

    # # the concatenated for the final png
    pout1 = Path(mkdir_p(join(pout, 'concatenated', '')))
    # # create the png image and delete the tex and intermediate results.
    cmd = ('cd {0}; pdflatex {1}.tex; pdfcrop {1}.pdf;'
           'rm {1}.aux {1}.log {1}.pdf; mv {1}-crop.pdf {2}.pdf;'
           'pdftoppm -png {2}.pdf > {2}.png; rm {2}.pdf; rm {0}*.png; rm {0}*.tex')
    nconc = pout1.stem + sep + nlat
    system(cmd.format(pout, nlat, nconc))
