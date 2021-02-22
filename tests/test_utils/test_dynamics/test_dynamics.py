import numpy as np

from hysynth.utils.dynamics import *


def test_constant():
    b = np.array([2.0, 3.0])
    dyn = ConstDyn(b)
    x0 = np.array([1.0, 4.0])
    x1 = dyn.successor(t=2.0, x0=x0)
    print(x1)
    assert dyn.dim() == 2
    assert np.isclose(x1, np.array([5.0, 10.0])).all()


def test_linear():
    A = np.array([[1.0, 1.0], [0.0, 1.0]])
    dyn = LinDyn(A)
    x0 = np.array([2.0, 4.0])
    x1 = dyn.successor(t=2.0, x0=x0)
    assert dyn.dim() == 2
    assert np.isclose(x1, np.array([73.89056099, 29.5562244])).all()


def test_affine():
    A = np.array([[1.0, 1.0], [0.0, 1.0]])
    b = np.array([2.0, 3.0])
    dyn = AffDyn(A, b)
    x0 = np.array([2.0, 4.0])
    x1 = dyn.successor(t=2.0, x0=x0)
    assert dyn.dim() == 2
    assert np.isclose(x1, np.array([111.83584148,  48.72339269])).all()


if __name__ == "__main__":
    test_constant()
    test_linear()
    test_affine()
