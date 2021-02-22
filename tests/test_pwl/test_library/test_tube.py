import pytest
import ppl
from numpy.testing import assert_allclose

from hysynth.pwl.library import tube


def test_tube():
    t = ppl.Variable(0)
    x1 = ppl.Variable(1)
    x2 = ppl.Variable(2)

    # 1D zigzag function
    f = [[0., 0.], [1., 1.], [2., 0.], [3., 1.]]
    actual_tube = tube(f, delta=0.1)

    et1 = ppl.NNC_Polyhedron(2, 'universe')
    et1.add_constraint(-t >= -1)
    et1.add_constraint(1*t >= 0)
    et1.add_constraint(-10*t + 10*x1 >= -1)
    et1.add_constraint(10*t - 10*x1 >= -1)

    et2 = ppl.NNC_Polyhedron(2, 'universe')
    et2.add_constraint(-t >= -2)
    et2.add_constraint(1*t >= 1)
    et2.add_constraint(-10*t - 10*x1 >= -21)
    et2.add_constraint(10*t + 10*x1 >= 19)

    et3 = ppl.NNC_Polyhedron(2, 'universe')
    et3.add_constraint(-t >= -3)
    et3.add_constraint(1*t >= 2)
    et3.add_constraint(-10*t + 10*x1 >= -21)
    et3.add_constraint(10*t - 10*x1 >= 19)

    expected_tube = [et1, et2, et3]
    for i in range(len(f)-1):
        assert actual_tube[i] == expected_tube[i]

    # 2D zigzag function
    f = [[0., 0., 1.], [1., 1., 0.], [2., 0., 1.]]
    actual_tube = tube(f, delta=0.1)

    et1 = ppl.NNC_Polyhedron(3, 'universe')
    et1.add_constraint(-t >= -1)
    et1.add_constraint(1*t >= 0)
    et1.add_constraint(-10*t + 10*x1 >= -1)
    et1.add_constraint(10*t - 10*x1 >= -1)
    et1.add_constraint(10*t + 10*x2 >= 9)
    et1.add_constraint(-10*t - 10*x2 >= -11)

    et2 = ppl.NNC_Polyhedron(3, 'universe')
    et2.add_constraint(-t >= -2)
    et2.add_constraint(1*t >= 1)
    et2.add_constraint(-10*t - 10*x1 >= -21)
    et2.add_constraint(10*t + 10*x1 >= 19)
    et2.add_constraint(10*t - 10*x2 >= 9)
    et2.add_constraint(-10*t + 10*x2 >= -11)

    expected_tube = [et1, et2]
    for i in range(len(f)-1):
        assert actual_tube[i] == expected_tube[i]
