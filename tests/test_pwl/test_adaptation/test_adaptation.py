import ppl

import hysynth.pwl.membership.parma_mem as pmem
import hysynth.pwl.adaptation.modecreation as mc
from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwl import library as lib


def two_modes_no_cycle(pwl_function):

    # Definition of the hybrid automaton
    # slopes
    m1 = [1.]
    m2 = [-1.]

    # variables
    t = ppl.Variable(0)
    x = ppl.Variable(1)

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 5)

    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 5)

    # guard
    G12 = ppl.NNC_Polyhedron(2,'universe')
    G12.add_constraint(2*x >= 9)
    G12.add_constraint(x <= 5)

    # hybrid automaton
    hs = HybridSystemPolyhedral("Test1", ["var1"])

    for loc in ["loc1", "loc2"]:
        hs.add_location(location_name=loc)

    hs.set_invariant("loc1", I1)
    hs.set_invariant("loc2", I2)

    hs.set_flow("loc1", m1)
    hs.set_flow("loc2", m2)

    hs.add_edge("loc1", "loc2")

    hs.set_guard(("loc1", "loc2"), G12)

    # delta
    delta = 0.25
    ftube = lib.tube(pwl_function, delta)
    membership, info = pmem.membership_info(pwl_function, hs, ftube)

    if membership:
        return hs

    info_part = max(info, key=lambda x: x[3])

    return mc.modecreation_main(pwl_function, info_part[0], info_part[1], info_part[2], hs, info_part[3], info_part[4], 1)


def test_returns_hs_1():
    f1 = [[0., 0.], [5., 5.], [10., 5.]]
    hs1 = two_modes_no_cycle(f1)
    assert isinstance(hs1, HybridSystemPolyhedral)


def test_returns_hs_2():
    f2 = [[0., 5.], [5., 0.], [10., 0.]]
    hs2 = two_modes_no_cycle(f2)
    assert isinstance(hs2, HybridSystemPolyhedral)


def test_returns_hs_3():
    f3 = [[0., 5.], [5., 0.], [10., 5.]]
    hs3 = two_modes_no_cycle(f3)
    assert isinstance(hs3, HybridSystemPolyhedral)
