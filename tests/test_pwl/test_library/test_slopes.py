import pytest
from numpy.testing import assert_allclose

from hysynth.pwl.library import slopes


def test_slopes():
    # 1D zigzag function
    f = [[0., 0.], [1., 1.], [2., 0.], [3., 1.]]
    assert slopes(f) == [[1.], [-1.], [1.]]

    # 2D zigzag function
    f = [[0., 0., 1.], [1., 1., 0.], [2., 0., 1.], [3., 1., 0.]]
    assert slopes(f) == [[1., -1.], [-1., 1.], [1., -1.]]

    # 3D random function with different time steps
    f = [[0., 0., 0.], [0.5, 1., 0.], [2., 0.4, 0.9], [3., 0.4, 1.23]]
    assert_allclose(slopes(f), [[2., 0.], [-0.4, 0.6], [0., 0.33]])
