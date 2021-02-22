import ppl

from hysynth.pwl import library as lib
from hysynth.pwl.membership.parma_mem import path_membership_info
from hysynth.pwl.adaptation import relax_ha
from hysynth.utils.hybrid_system import HybridSystemPolyhedral


def test_three_piece():
    r""" TEST: three-piece time series of shape '/\_' that can be relaxed"""
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # PWL function
    f = [[0., 0.], [1., 3.], [2., 0.], [3., 0.]]

    # delta
    delta = 1.

    # hybrid automaton
    ha = HybridSystemPolyhedral("Test", ["var1"], delta=delta)

    # locations
    for loc in ["Q1", "Q2", "Q3"]:
        ha.add_location(location_name=loc)

    # slopes
    ha.set_flow("Q1", [1.])
    ha.set_flow("Q2", [-1.])
    ha.set_flow("Q3", [0.])

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0. - delta)
    I1.add_constraint(x <= 1. + delta)
    ha.set_invariant("Q1", I1)  # 0-δ ≤ x ≤ 1+δ
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0. - delta)
    I2.add_constraint(x <= 1. + delta)
    ha.set_invariant("Q2", I2)  # 0-δ ≤ x ≤ 1+δ
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= 0. - delta)
    I3.add_constraint(x <= 0. + delta)
    ha.set_invariant("Q3", I3)  # -δ ≤ x ≤ δ

    # transition from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(10. * x - 8. >= 0)
    G12.add_constraint(10. * x - 10. <= 0)
    ha.add_edge("Q1", "Q2")
    ha.set_guard(("Q1", "Q2"), G12)  # 0.8 ≤ x ≤ 1

    # transition from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 0.)
    G23.add_constraint(x - 2. <= 0.)
    ha.add_edge("Q2", "Q3")
    ha.set_guard(("Q2", "Q3"), G23)  # 0 ≤ x ≤ 2

    # path
    path = ["Q1", "Q2", "Q3"]

    ftube = lib.tube(f, delta)
    answer, ftube, Aa, Bb, j = path_membership_info(f, path, ha, ftube)
    assert answer is False

    result = relax_ha(f, ha, ftube)  # expected: relaxed automaton
    assert result is not None


def test_two_piece():
    r""" TEST: two-piece time series of shape '\_' that cannot be relaxed"""
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # PWL function
    f = [[0., 0.], [1., -5.], [2., -5.]]

    # delta
    delta = 1.

    # hybrid automaton
    ha = HybridSystemPolyhedral("Test", ["var1"], delta=delta)

    # locations
    for loc in ["Q1", "Q2"]:
        ha.add_location(location_name=loc)

    # slopes
    ha.set_flow("Q1", [1.])
    ha.set_flow("Q2", [0.])

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0.)
    ha.set_invariant("Q1", I1)  # x ≥ 0
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0.)
    ha.set_invariant("Q1", I2)  # x ≥ 0

    # transition from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 0.)
    ha.add_edge("Q1", "Q2")
    ha.set_guard(("Q1", "Q2"), G12)  # x ≥ 0

    # path
    path = ["Q1", "Q2"]

    ftube = lib.tube(f, delta)
    answer, ftube, Aa, Bb, j = path_membership_info(f, path, ha, ftube)
    assert answer is False

    result = relax_ha(f, ha, ftube)
    assert result is None


def test_one_piece():
    r""" TEST: one-piece time series of shape '\' that can be relaxed"""
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # PWL function
    f = [[0., 0.], [2., -2.]]

    # delta
    delta = 1.

    # hybrid automaton
    ha = HybridSystemPolyhedral("Test", ["var1"], delta=delta)

    # locations
    for loc in ["Q1"]:
        ha.add_location(location_name=loc)

    # slopes
    ha.set_flow("Q1", [-1.])

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0.)
    ha.set_invariant("Q1", I1)  # x ≥ 0

    # path
    path = ["Q1"]

    ftube = lib.tube(f, delta)
    answer, _, Aa, Bb, j = path_membership_info(f, path, ha, ftube)
    assert answer is False

    result = relax_ha(f, ha, ftube)  # expected: relaxed automaton
    assert result is not None
