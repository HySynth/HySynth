import ppl

from hysynth.pwl import library as lib
import hysynth.pwl.membership.parma_mem as pmem
from hysynth.utils.hybrid_system import HybridSystemPolyhedral


def test_fourpiece_no_inv():
    """ TEST: four-piece time series, no invariants	"""
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # PWL function
    f = [[0., 0.25], [1., 1.25], [3., 1.25], [4., 1.75], [6., -0.25]]

    # hybrid automaton
    hs = HybridSystemPolyhedral("Test1", ["var1"])

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I4 = ppl.NNC_Polyhedron(2, 'universe')

    for loc in ["Q1", "Q2", "Q3", "Q4"]:
        hs.add_location(location_name=loc)

    hs.set_invariant("Q1", I1)
    hs.set_invariant("Q2", I2)
    hs.set_invariant("Q3", I3)
    hs.set_invariant("Q4", I4)

    # slopes
    m1 = [0.5]
    m2 = [0.2]
    m3 = [0.5]
    m4 = [-1.8]
    # m4 = -1.

    hs.set_flow("Q1", m1)
    hs.set_flow("Q2", m2)
    hs.set_flow("Q3", m3)
    hs.set_flow("Q4", m4)

    # guard from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x - 1 >= 0)

    # guard from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(10 * x - 13 >= 0)

    # guard from 3 to 4
    G34 = ppl.NNC_Polyhedron(2, 'universe')
    G34.add_constraint(10 * x - 14 >= 0)

    hs.add_edge("Q1", "Q2")
    hs.add_edge("Q2", "Q3")
    hs.add_edge("Q3", "Q4")

    hs.set_guard(("Q1", "Q2"), G12)
    hs.set_guard(("Q2", "Q3"), G23)
    hs.set_guard(("Q3", "Q4"), G34)

    # guard after last transition (empty set)
    # G4e = ppl.NNC_Polyhedron(2, 'empty')   # how to deal with this!

    # path
    path = ["Q1", "Q2", "Q3", "Q4"]

    # delta
    delta = 0.25
    ftube = lib.tube(f, delta)
    result = pmem.path_membership_info(f, path, hs, ftube)

    assert False is result[0]


def test_three_piece():
    """ TEST: three-piece time series """
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # PWL function
    f = [[0., 2.], [1., 1.], [2., 0.], [3., 0.]]

    # hybrid automaton
    # hybrid automaton
    hs1 = HybridSystemPolyhedral("Test2", ["var1"])

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I3 = ppl.NNC_Polyhedron(2, 'universe')

    for loc in ["Q1", "Q2", "Q3"]:
        hs1.add_location(location_name=loc)

    hs1.set_invariant("Q1", I1)
    hs1.set_invariant("Q2", I2)
    hs1.set_invariant("Q3", I3)

    # slopes
    m1 = [-0.9]
    m2 = [-1.1]
    m3 = [0.]

    hs1.set_flow("Q1", m1)
    hs1.set_flow("Q2", m2)
    hs1.set_flow("Q3", m3)

    # guard from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(10 * x - 12 >= 0)
    G12.add_constraint(10 * x - 15 <= 0)

    # guard from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(10 * x + 1 <= 0)

    hs1.add_edge("Q1", "Q2")
    hs1.add_edge("Q2", "Q3")

    hs1.set_guard(("Q1", "Q2"), G12)
    hs1.set_guard(("Q2", "Q3"), G23)

    # path
    path = ["Q1", "Q2", "Q3"]

    # delta
    delta = 0.3
    ftube = lib.tube(f, delta)
    result = pmem.path_membership_info(f, path, hs1, ftube)
    assert True is result[0]


def test_three_piece_1():
    # PWL function
    f = [[0., 0.], [4., 4.], [6., 2.], [10., 2.]]

    # Data from the hybrid automaton
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # hybrid automaton
    hs2 = HybridSystemPolyhedral("Test3", ["var1"])

    # Invariant 1
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= -1)
    I1.add_constraint(x <= 5)

    # Invariant 2
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= -1)
    I2.add_constraint(x <= 5)

    # Invariant 3
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= -1)
    I3.add_constraint(x <= 5)

    for loc in ["Q1", "Q2", "Q3"]:
        hs2.add_location(location_name=loc)

    hs2.set_invariant("Q1", I1)
    hs2.set_invariant("Q2", I2)
    hs2.set_invariant("Q3", I3)

    # Guard from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 3)
    G12.add_constraint(x <= 5)

    # Guard from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 1)
    G23.add_constraint(x <= 3)

    hs2.add_edge("Q1", "Q2")
    hs2.add_edge("Q2", "Q3")

    hs2.set_guard(("Q1", "Q2"), G12)
    hs2.set_guard(("Q2", "Q3"), G23)

    # Dynamics - slope
    m1 = [1.]
    m2 = [-1.]
    m3 = [0.]

    hs2.set_flow("Q1", m1)
    hs2.set_flow("Q2", m2)
    hs2.set_flow("Q3", m3)

    path = ["Q1", "Q2", "Q3"]

    delta = 1.
    ftube = lib.tube(f, delta)
    result = pmem.path_membership_info(f, path, hs2, ftube)

    assert True is result[0]


def test_three_piece_2():
    # PWL function
    f = [[0., 0.], [4., 4.], [6., 2.], [10., 2.]]

    # Data from the hybrid automaton
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    hs3 = HybridSystemPolyhedral("Test2", ["var1"])

    # Invariant 1
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= -1)
    I1.add_constraint(x <= 5)

    # Invariant 2
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(2 * x >= 7)  # G1.add_constraint(x >= 3.5)
    I2.add_constraint(x <= 5)

    # Invariant 3
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= -1)
    I3.add_constraint(x <= 5)

    for loc in ["Q1", "Q2", "Q3"]:
        hs3.add_location(location_name=loc)

    hs3.set_invariant("Q1", I1)
    hs3.set_invariant("Q2", I2)
    hs3.set_invariant("Q3", I3)

    # Guard from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(2 * x >= 7)  # G12.add_constraint(x >= 3.5)
    G12.add_constraint(x <= 5)

    # Guard from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 1)
    G23.add_constraint(x <= 3)

    hs3.add_edge("Q1", "Q2")
    hs3.add_edge("Q2", "Q3")

    hs3.set_guard(("Q1", "Q2"), G12)
    hs3.set_guard(("Q2", "Q3"), G23)

    # Dynamics - slope
    m1 = [1.]
    m2 = [-1.]
    m3 = [0.]

    hs3.set_flow("Q1", m1)
    hs3.set_flow("Q2", m2)
    hs3.set_flow("Q3", m3)

    path = ["Q1", "Q2", "Q3"]

    delta = 1.
    ftube = lib.tube(f, delta)
    result = pmem.path_membership_info(f, path, hs3, ftube)

    assert False is result[0]


def test_three_piece_3():
    # PWL function
    f = [[0., 0.], [4., 4.], [6., 2.], [10., 2.]]

    # Data from the hybrid automaton
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    hs4 = HybridSystemPolyhedral("Test3", ["var1"])

    # Invariant 1
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= -1)
    I1.add_constraint(x <= 5)

    # Invariant 2
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= -1)
    I2.add_constraint(x <= 5)

    # Invariant 3
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= -1)
    I3.add_constraint(x <= 5)

    for loc in ["Q1", "Q2", "Q3"]:
        hs4.add_location(location_name=loc)

    hs4.set_invariant("Q1", I1)
    hs4.set_invariant("Q2", I2)
    hs4.set_invariant("Q3", I3)

    # Guard from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 4)
    G12.add_constraint(x <= 5)

    # Guard from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 1)
    G23.add_constraint(x <= 2)

    hs4.add_edge("Q1", "Q2")
    hs4.add_edge("Q2", "Q3")

    hs4.set_guard(("Q1", "Q2"), G12)
    hs4.set_guard(("Q2", "Q3"), G23)

    # Dynamics - slope
    m1 = [1.]
    m2 = [-1.]
    m3 = [0.]

    hs4.set_flow("Q1", m1)
    hs4.set_flow("Q2", m2)
    hs4.set_flow("Q3", m3)

    path = ["Q1", "Q2", "Q3"]

    delta = 1.
    ftube = lib.tube(f, delta)
    result = pmem.path_membership_info(f, path, hs4, ftube)

    assert True is result[0]


def test_three_piece_4():
    # PWL function
    f = [[0., 0.], [4., 4.], [6., 2.], [10., 2.]]

    # Data from the hybrid automaton
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    hs5 = HybridSystemPolyhedral("Test2", ["var1"])

    # Invariant 1
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= -1)
    I1.add_constraint(x <= 5)

    # Invariant 2
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= -1)
    I2.add_constraint(x <= 5)

    # Invariant 3
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= -1)
    I3.add_constraint(x <= 5)

    for loc in ["Q1", "Q2", "Q3"]:
        hs5.add_location(location_name=loc)

    hs5.set_invariant("Q1", I1)
    hs5.set_invariant("Q2", I2)
    hs5.set_invariant("Q3", I3)

    # Guard from 1 to 2
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(2 * x >= 9)  # G1.add_constraint(x >= 4.5)
    G12.add_constraint(x <= 5)

    # Guard from 2 to 3
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 1)
    G23.add_constraint(x <= 2)

    hs5.add_edge("Q1", "Q2")
    hs5.add_edge("Q2", "Q3")

    hs5.set_guard(("Q1", "Q2"), G12)
    hs5.set_guard(("Q2", "Q3"), G23)

    # Dynamics - slope
    m1 = [1.]
    m2 = [-1.]
    m3 = [0.]

    hs5.set_flow("Q1", m1)
    hs5.set_flow("Q2", m2)
    hs5.set_flow("Q3", m3)

    path = ["Q1", "Q2", "Q3"]

    delta = 1.
    ftube = lib.tube(f, delta)
    result = pmem.path_membership_info(f, path, hs5, ftube)

    assert True is result[0]
