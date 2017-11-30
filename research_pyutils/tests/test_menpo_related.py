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
    # ensure that the landmarks are reversed as well (though NOT semantically correct):
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
    # TODO: ideally here more tests that check random points, e.g. the
    # transformation of point 0 in the flipped. Also, more cases.
    # # d) check 15 random points.
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

