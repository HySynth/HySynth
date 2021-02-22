import ppl

from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


def two_mode_p1_m1_ha():
    """ Simple zig zag automaton """
    ha = HybridSystemPolyhedral(name="TwoMode +1 -1",
                                variable_names=[get_var(1)],
                                delta=0.1)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 2)
    I1.add_constraint(x <= 7)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [1.])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 1)
    I2.add_constraint(x <= 9)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [-1.])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 5)
    G12.add_constraint(x <= 7)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 2)
    G21.add_constraint(x <= 3)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


def two_mode_p1_m1_same_constraints_ha():
    """ simple zig zag automaton with the same constraints everywhere """
    ha = HybridSystemPolyhedral(name="TwoMode +1 -1 same constraints",
                                variable_names=[get_var(1)],
                                delta=0.1)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 10)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [1.])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 10)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [-1.])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 0)
    G12.add_constraint(x <= 10)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 0)
    G21.add_constraint(x <= 10)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


def two_mode_p001_m001_ha():
    """ Simple zig zag automaton with slopes close to 0 """
    ha = HybridSystemPolyhedral(name="TwoMode +0.01 -0.01",
                                variable_names=[get_var(1)],
                                delta=0.1)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(10*x >= 2)
    I1.add_constraint(10*x <= 7)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [0.01])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(10*x >= 1)
    I2.add_constraint(10*x <= 9)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [-0.01])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(10*x >= 5)
    G12.add_constraint(10*x <= 7)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(10*x >= 2)
    G21.add_constraint(10*x <= 3)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


def two_mode_p1_0_ha():
    """ automaton with slopes 1 and 0 """
    ha = HybridSystemPolyhedral(name="TwoMode +1 0",
                                variable_names=[get_var(1)],
                                delta=0.1)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 5)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [1.])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 5)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [0.])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 1)
    G12.add_constraint(x <= 5)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 1)
    G21.add_constraint(x <= 5)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


def two_mode_p01_p02_ha():
    """ automaton with slopes 0.1 and 0.2 """
    ha = HybridSystemPolyhedral(name="TwoMode +0.1 +0.2",
                                variable_names=[get_var(1)],
                                delta=0.1)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 5)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [0.0001])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 5)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [0.2])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 1)
    G12.add_constraint(x <= 2)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 2)
    G21.add_constraint(x <= 3)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


def three_mode_p1_m1_m05_ha():
    """automaton with slopes 1, -1, and -0.5"""
    ha = HybridSystemPolyhedral(name="ThreeMode +1 -1 -0.5",
                                variable_names=[get_var(1)],
                                delta=0.05)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 10)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [1.])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 10)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [-1.])

    ha.add_location("Q3")
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= 0)
    I3.add_constraint(x <= 10)
    ha.set_invariant("Q3", I3)
    ha.set_flow("Q3", [-0.5])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 5)
    G12.add_constraint(x <= 10)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q3")
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 0)
    G23.add_constraint(x <= 5)
    ha.set_guard(("Q2", "Q3"), G23)

    ha.add_edge(from_location="Q3", to_location="Q1")
    G31 = ppl.NNC_Polyhedron(2, 'universe')
    G31.add_constraint(x >= 5)
    G31.add_constraint(x <= 6)
    ha.set_guard(("Q3", "Q1"), G31)

    return ha


def three_mode_p1_m1_0_ha():
    """automaton with slopes 1, -1, and 0 (in a dead end)"""
    ha = HybridSystemPolyhedral(name="ThreeMode +1 -1 0",
                                variable_names=[get_var(1)],
                                delta=0.2)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 10)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [1.])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 10)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [-1.])

    ha.add_location("Q3")
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= 5)
    I3.add_constraint(x <= 7)
    ha.set_invariant("Q3", I3)
    ha.set_flow("Q3", [0.])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 5)
    G12.add_constraint(x <= 10)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 0)
    G21.add_constraint(x <= 5)
    ha.set_guard(("Q2", "Q1"), G21)

    ha.add_edge(from_location="Q1", to_location="Q3")
    G13 = ppl.NNC_Polyhedron(2, 'universe')
    G13.add_constraint(x >= 6)
    G13.add_constraint(x <= 7)
    ha.set_guard(("Q1", "Q3"), G13)

    ha.add_edge(from_location="Q2", to_location="Q3")
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 5)
    G23.add_constraint(x <= 6)
    ha.set_guard(("Q2", "Q3"), G23)

    return ha


def four_mode_p2_m1_p1_m2_ha():
    """automaton with slopes 2, -1, 1, -2"""
    ha = HybridSystemPolyhedral(name="FourMode +2 -1 +1 -2",
                                variable_names=[get_var(1)],
                                delta=0.2)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 10)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", [2.])

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 10)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", [-1.])

    ha.add_location("Q3")
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= 0)
    I3.add_constraint(x <= 10)
    ha.set_invariant("Q3", I3)
    ha.set_flow("Q3", [1.])

    ha.add_location("Q4")
    I4 = ppl.NNC_Polyhedron(2, 'universe')
    I4.add_constraint(x >= 0)
    I4.add_constraint(x <= 10)
    ha.set_invariant("Q4", I4)
    ha.set_flow("Q4", [-2.])

    # transitions
    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 5)
    G12.add_constraint(x <= 10)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 0)
    G21.add_constraint(x <= 2)
    ha.set_guard(("Q2", "Q1"), G21)

    ha.add_edge(from_location="Q2", to_location="Q3")
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= 3)
    G23.add_constraint(x <= 7)
    ha.set_guard(("Q2", "Q3"), G23)

    ha.add_edge(from_location="Q3", to_location="Q2")
    G32 = ppl.NNC_Polyhedron(2, 'universe')
    G32.add_constraint(x >= 3)
    G32.add_constraint(x <= 7)
    ha.set_guard(("Q3", "Q2"), G32)

    ha.add_edge(from_location="Q3", to_location="Q4")
    G34 = ppl.NNC_Polyhedron(2, 'universe')
    G34.add_constraint(x >= 8)
    G34.add_constraint(x <= 10)
    ha.set_guard(("Q3", "Q4"), G34)

    ha.add_edge(from_location="Q4", to_location="Q3")
    G43 = ppl.NNC_Polyhedron(2, 'universe')
    G43.add_constraint(x >= 0)
    G43.add_constraint(x <= 5)
    ha.set_guard(("Q4", "Q3"), G43)

    return ha
