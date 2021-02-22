import pytest
import ppl

from hysynth.pwl.library import post


def test_post():
    t = ppl.Variable(0)
    x1 = ppl.Variable(1)
    x2 = ppl.Variable(2)

    p1 = ppl.NNC_Polyhedron(2, 'universe')
    p1.add_constraint(2*t >= 1)
    p1.add_constraint(t <= 1)
    p1.add_constraint(2*x1 >= 3)
    p1.add_constraint(x1 <= 2)

    p2 = ppl.NNC_Polyhedron(2, 'universe')
    p2.add_constraint(t + x1 >= 1)
    p2.add_constraint(t + x1 <= 5)
    p2.add_constraint(t - x1 >= 2)
    p2.add_constraint(t - x1 <= 3)

    flow = [-1.]

    reach = post(p1, p2, flow)

    expected_reach = ppl.NNC_Polyhedron(2, 'universe')
    expected_reach.add_constraint(t + x1 <= 3)
    expected_reach.add_constraint(t - x1 >= 2)
    expected_reach.add_constraint(t + x1 >= 2)
    expected_reach.add_constraint(t - x1 <= 3)

    assert reach == expected_reach

    p1 = ppl.NNC_Polyhedron(3, 'universe')
    p1.add_constraint(t == 0)
    p1.add_constraint(2*x1 >= 1)
    p1.add_constraint(x1 <= 1)
    p1.add_constraint(2*x2 >= 3)
    p1.add_constraint(x2 <= 2)

    p2 = ppl.NNC_Polyhedron(3, 'universe')
    p1.add_constraint(t >= 0)
    p1.add_constraint(t <= 5)
    p2.add_constraint(x1 + x2 >= 1)
    p2.add_constraint(x1 + x2 <= 5)
    p2.add_constraint(x1 - x2 >= 2)
    p2.add_constraint(x1 - x2 <= 3)

    flow = [1., -1.]

    reach = post(p1, p2, flow)

    assert isinstance(reach, ppl.NNC_Polyhedron)
