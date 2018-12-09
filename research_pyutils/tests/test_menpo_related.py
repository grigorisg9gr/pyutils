try:
    import menpo.io as mio
except ImportError:
    # # effort 1 to achieve skipping the tests when menpo does not exist:
    # # https://stackoverflow.com/a/12488542/1716869
    from unittest import SkipTest
    msg = 'Menpo libary was not imported, skipping the tests in {}'
    SkipTest(msg.format(__file__))
import numpy as np
glob_im = mio.import_builtin_asset.lenna_png()
# # lambda function for ensuring the equality of menpo image shapes.
im_shape = lambda im: np.array(im.pixels.shape)
shape_eq = lambda im1, im2: np.all(im_shape(im1) == im_shape(im2))


def test_flip_images():
    from research_pyutils import flip_images
    im = glob_im.copy()
    ims = flip_images(im)
    assert len(ims) == 1
    # get the pure mirror.
    mirror = im.mirror()
    assert np.allclose(ims[0].pixels, mirror.pixels)
    # ensure that the landmarks are reversed as well (although semantically correct ONLY in
    # the case of ibug68 by default):
    # a) not the same as the original.
    gr = im.landmarks.group_labels[0]
    lms = ims[0].landmarks[gr].lms
    assert not np.allclose(lms.points, im.landmarks[gr].lms.points)
    # b) not close with the pure mirror.
    assert not np.allclose(lms.points, mirror.landmarks[gr].lms.points)
    # c) by reversing the flip, we should end up in the same.
    ims2 = flip_images(ims)
    lms = ims2[0].landmarks[gr].lms
    assert np.allclose(lms.points, im.landmarks[gr].lms.points)
    # # Check that few random pixels are reversed appropriately.
    for _ in range(15):
        # sample random values for row, column check.
        r = np.random.randint(0, im.shape[0])
        c = np.random.randint(0, im.shape[1])
        value = im.pixels[0, r, c]
        # # check now the mirrored one (only the column is changing).
        c_fl = im.shape[1] - c - 1
        value_fl = ims[0].pixels[0, r, c_fl]
        # # ensure that they are indeed close.
        assert np.allclose(value, value_fl)


def test_resize_all_images():
    from research_pyutils import resize_all_images
    # # import the assets.
    c = mio.import_builtin_asset
    ims = [c.lenna_png(), c.takeo_ppm(), c.einstein_jpg()]

    cc = resize_all_images(ims)
    m = np.min([im.shape for im in ims], axis=0)
    # check that the number of rows is indeed the min.
    assert(np.all(cc[0].shape == m))
    # ensure that it's smaller than the original
    assert(np.all(cc[0].shape <= ims[0].shape))

    # apply a different function
    f = lambda sizes: np.median(sizes, axis=0)
    cc1 = resize_all_images(ims, f)
    assert(np.all(cc1[0].shape >= cc[0].shape))
    assert(np.all(cc1[1].shape >= cc[1].shape))

    # apply a fixed size function
    f = lambda sizes: np.array([900, 200])
    cc2 = resize_all_images(ims, f)
    assert(cc2[0].shape[0] == 900)
    assert(cc2[1].shape[1] == 200)


def test_compute_overlap():
    from research_pyutils import compute_overlap
    # import a builtin landmark file
    ln = mio.import_builtin_asset.lenna_ljson()

    # convert it first to a bounding box:
    bb0 = ln.lms.bounding_box()
    # first test with same overlap.
    ov1 = compute_overlap(bb0.points, bb0.points)
    assert np.allclose(ov1, 1.)
    # test now the bb vs the ln points
    ov2 = compute_overlap(bb0.points, ln.lms.points)
    assert np.allclose(ov2, 1.)

    bb1 = bb0.points - 400
    ov3 = compute_overlap(bb0.points, bb1)
    assert np.allclose(ov3, 0.)


def test_compute_overlap_fake_bb():
    from research_pyutils import compute_overlap
    from menpo.shape import bounding_box
    # # create two bounding boxes.
    bb1 = bounding_box((0, 0), (1, 1))
    bb2 = bounding_box((0, 0), (1.5, 1.5))
    # # compute the overlap and ensure it has the appropriate value.
    ov1 = compute_overlap(bb1.points, bb2.points)
    assert np.abs(ov1 - 0.64) < 0.0001


def test_get_segment_image_single_semgnet():
    from research_pyutils import get_segment_image
    im = glob_im.copy()
    im_segm = get_segment_image(im, 1, 1)
    assert shape_eq(im, im_segm), '{} {}'.format(im.shape, im_segm.shape)


def test_get_segment_image_two_semgnets():
    from research_pyutils import get_segment_image
    im = glob_im.copy()
    im_segm = get_segment_image(im, 1, 2)
    # # format the original shape to match the new one.
    shape_org = im_shape(im)
    shape_org[1] //= 2
    assert np.all(shape_org == im_shape(im_segm))
    # # also check the content to match.
    diff = im.pixels[:, :shape_org[1]] - im_segm.pixels
    assert np.all(np.abs(diff) < 0.0001)

    # # perform the actions again for segment two.
    im_segm2 = get_segment_image(im, 2, 2)
    assert np.all(shape_org == im_shape(im_segm2))
    # # also check the content to match.
    diff = im.pixels[:, shape_org[1]:] - im_segm2.pixels
    assert np.all(np.abs(diff) < 0.0001)


def test_get_segment_image_two_semgnets_diff_axis():
    from research_pyutils import get_segment_image
    im = glob_im.copy()
    im_segm = get_segment_image(im, 1, 2, axis=2)
    # # format the original shape to match the new one.
    shape_org = im_shape(im)
    shape_org[2] //= 2
    assert np.all(shape_org == im_shape(im_segm))


def test_get_segment_image_three_semgnets_imprecise_div():
    from research_pyutils import get_segment_image
    im = glob_im.copy()
    im_segm = get_segment_image(im, 1, 3, axis=2)
    # # format the original shape to match the new one.
    shape_org = im_shape(im)
    shape_org[2] //= 3
    assert np.all(shape_org == im_shape(im_segm))


def test_access_ln_frame_simple():
    from research_pyutils import access_ln_frame
    # # define a dummy matrix.
    mat = np.random.rand(10, 68, 2)
    # # call the access_ln_frame and assert the
    # # similarity of the results.
    row = access_ln_frame(mat, {}, idx=2)
    assert np.allclose(mat[2], row.points)
    # # define a tensor of more dims and use the same function.
    mat2 = np.random.rand(10, 68, 4, 4, 3)
    # # call the access_ln_frame and assert the
    # # similarity of the results.
    row = access_ln_frame(mat2, {}, idx=9)
    assert np.allclose(mat2[9], row.points)


def test_concatenate_all_ims_from_list():
    from research_pyutils import concatenate_all_ims_from_list
    im = glob_im.copy()
    ims = [im, im, im]

    # # # # # case 1: horizontal concat. # # # # #
    im_c = concatenate_all_ims_from_list(ims)
    # # check the sizes of the images.
    sh_i = im.pixels.shape
    sh_c = im_c.pixels.shape
    cond = (sh_i[0] == sh_c[0]) and (sh_i[1] == sh_c[1]) and (sh_i[2] * len(ims) == sh_c[2])
    assert cond
    # # ensure they have same pixels.
    assert np.all(im_c.pixels[:, :, :sh_i[2]] == im.pixels)

    # # # # # case 2: vertical concat. # # # # #
    im_c = concatenate_all_ims_from_list(ims, axis=1)
    # # check the sizes of the images.
    sh_i = im.pixels.shape
    sh_c = im_c.pixels.shape
    cond = (sh_i[0] == sh_c[0]) and (sh_i[1] * len(ims) == sh_c[1]) and (sh_i[2] == sh_c[2])
    assert cond

    # # # # # case 3: single image # # # # #
    ims = [im]
    im_c = concatenate_all_ims_from_list(ims, axis=1)
    # # check the sizes of the images.
    sh_i = im.pixels.shape
    sh_c = im_c.pixels.shape
    cond = (sh_i[0] == sh_c[0]) and (sh_i[1] == sh_c[1]) and (sh_i[2] == sh_c[2])
    assert cond
    assert np.all(im_c.pixels == im.pixels)
