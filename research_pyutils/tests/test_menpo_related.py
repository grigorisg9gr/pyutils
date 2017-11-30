try:
    import menpo.io as mio
except ImportError:
    assert 0, 'Message must be printed here, also scheme to skip these tests.'
import numpy as np


def test_flip_images():
    from research_pyutils import flip_images
    im = mio.import_builtin_asset.lenna_png()
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

