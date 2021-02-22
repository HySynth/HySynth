import pytest
import ppl

from hysynth.pwl.library import get_intervals


def test_get_intervals():
    p1 = ppl.NNC_Polyhedron(2, 'universe')
    x = ppl.Variable(1)
    p1.add_constraint(x >= 1)
    p1.add_constraint(x <= 5)
    intervals = get_intervals(p1)
    assert intervals == [[1, 5]]

    p1 = ppl.NNC_Polyhedron(3, 'universe')
    y = ppl.Variable(2)
    p1.add_constraint(x >= 1)
    p1.add_constraint(x <= 5)
    p1.add_constraint(y >= 2)
    p1.add_constraint(y <= 4)
    intervals = get_intervals(p1)
    assert intervals == [[1, 5], [2, 4]]
