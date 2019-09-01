import numpy as np

def test_array_reshape_to_dims():
    from research_pyutils import array_reshape_to_dims
    a = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    sh = a.shape
    tot = sh[0] * sh[1]

    # # test 1 for a conversion, vectorize.
    b = array_reshape_to_dims(a, k=1)
    assert b.shape[0] == tot
    assert b[0] == a[0, 0] and b[-1] == a[-1, -1]
    assert np.all(b.reshape(sh) == a)

    # # test 2: convert to particular shape.
    b = array_reshape_to_dims(b, sh[1], sh[0], k=2)
    assert b.shape[0] == sh[1] and  b.shape[1] == sh[0]
    assert np.all(b.flatten().reshape(sh) == a)
    assert len(b.shape) == 2

    # # test 3: convert to particular shape.
    b = array_reshape_to_dims(b, sh[1], sh[0], k=3)
    assert b.shape[0] == sh[1] and  b.shape[1] == sh[0]
    assert np.all(b.flatten().reshape(sh) == a)
    assert len(b.shape) == 3

    # # test 4: convert to particular shape.
    b = array_reshape_to_dims(b, 1, tot)
    assert b.shape[1] == tot and b.shape[0] == 1
    assert np.all(b.flatten().reshape(sh) == a)
    assert len(b.shape) == 2

    # # reshape the original matrix a.
    a = a.reshape((2, 2, 2))
    sh = a.shape

    # # test 5: convert to particular shape.
    b = array_reshape_to_dims(b, 1, tot)
    assert b.shape[1] == tot and b.shape[0] == 1
    assert np.all(b.flatten().reshape(sh) == a)
    assert len(b.shape) == 2

    # # test 6 for a conversion, vectorize.
    b = array_reshape_to_dims(a, k=1)
    assert b.shape[0] == tot
    assert b[0] == a[0, 0, 0] and b[-1] == a[-1, -1, -1]
    assert np.all(b.reshape(sh) == a)

