import ppl

from hysynth.utils.hybrid_system import HybridSystemPolyhedral


def train_locations():
    ha = HybridSystemPolyhedral(name="Train with sequential speed-up",
                                variable_names=["var1"],
                                delta=0.2)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # locations
    ha.add_location("Q1")
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= -100)
    I1.add_constraint(x <= 100)
    ha.set_invariant("Q1", I1)
    ha.set_flow("Q1", {"var1": -0.2})

    ha.add_location("Q2")
    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= -100)
    I2.add_constraint(x <= 100)
    ha.set_invariant("Q2", I2)
    ha.set_flow("Q2", {"var1": 0})

    ha.add_location("Q3")
    I3 = ppl.NNC_Polyhedron(2, 'universe')
    I3.add_constraint(x >= -100)
    I3.add_constraint(x <= 100)
    ha.set_invariant("Q3", I3)
    ha.set_flow("Q3", {"var1": 0.3})

    ha.add_location("Q4")
    I4 = ppl.NNC_Polyhedron(2, 'universe')
    I4.add_constraint(x >= -100)
    I4.add_constraint(x <= 100)
    ha.set_invariant("Q4", I4)
    ha.set_flow("Q4", {"var1": 0.6})

    ha.add_location("Q5")
    I5 = ppl.NNC_Polyhedron(2, 'universe')
    I5.add_constraint(x >= -100)
    I5.add_constraint(x <= 100)
    ha.set_invariant("Q5", I5)
    ha.set_flow("Q5", {"var1": 0.9})

    return ha, x


def train_sequential_ha():
    """automaton with five modes connected as a doubly-linked chain (sequential speed)"""
    ha, x = train_locations()

    # transitions
    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= -100)
    G21.add_constraint(x <= 100)
    ha.set_guard(("Q2", "Q1"), G21)

    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= -100)
    G12.add_constraint(x <= 100)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q3")
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= -100)
    G23.add_constraint(x <= 100)
    ha.set_guard(("Q2", "Q3"), G23)

    ha.add_edge(from_location="Q3", to_location="Q2")
    G32 = ppl.NNC_Polyhedron(2, 'universe')
    G32.add_constraint(x >= -100)
    G32.add_constraint(x <= 100)
    ha.set_guard(("Q3", "Q2"), G32)

    ha.add_edge(from_location="Q3", to_location="Q4")
    G34 = ppl.NNC_Polyhedron(2, 'universe')
    G34.add_constraint(x >= -100)
    G34.add_constraint(x <= 100)
    ha.set_guard(("Q3", "Q4"), G34)

    ha.add_edge(from_location="Q4", to_location="Q3")
    G43 = ppl.NNC_Polyhedron(2, 'universe')
    G43.add_constraint(x >= -100)
    G43.add_constraint(x <= 100)
    ha.set_guard(("Q4", "Q3"), G43)

    ha.add_edge(from_location="Q4", to_location="Q5")
    G45 = ppl.NNC_Polyhedron(2, 'universe')
    G45.add_constraint(x >= -100)
    G45.add_constraint(x <= 100)
    ha.set_guard(("Q4", "Q5"), G45)

    ha.add_edge(from_location="Q5", to_location="Q4")
    G54 = ppl.NNC_Polyhedron(2, 'universe')
    G54.add_constraint(x >= -100)
    G54.add_constraint(x <= 100)
    ha.set_guard(("Q5", "Q4"), G54)

    return ha


def train_star_ha():
    """automaton with five modes connected as a star (instantaneous speed)"""
    ha, x = train_locations()

    # transitions
    ha.add_edge(from_location="Q2", to_location="Q1")
    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= -100)
    G21.add_constraint(x <= 100)
    ha.set_guard(("Q2", "Q1"), G21)

    ha.add_edge(from_location="Q1", to_location="Q2")
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= -100)
    G12.add_constraint(x <= 100)
    ha.set_guard(("Q1", "Q2"), G12)

    ha.add_edge(from_location="Q2", to_location="Q3")
    G23 = ppl.NNC_Polyhedron(2, 'universe')
    G23.add_constraint(x >= -100)
    G23.add_constraint(x <= 100)
    ha.set_guard(("Q2", "Q3"), G23)

    ha.add_edge(from_location="Q3", to_location="Q2")
    G32 = ppl.NNC_Polyhedron(2, 'universe')
    G32.add_constraint(x >= -100)
    G32.add_constraint(x <= 100)
    ha.set_guard(("Q3", "Q2"), G32)

    ha.add_edge(from_location="Q2", to_location="Q4")
    G24 = ppl.NNC_Polyhedron(2, 'universe')
    G24.add_constraint(x >= -100)
    G24.add_constraint(x <= 100)
    ha.set_guard(("Q2", "Q4"), G24)

    ha.add_edge(from_location="Q4", to_location="Q2")
    G42 = ppl.NNC_Polyhedron(2, 'universe')
    G42.add_constraint(x >= -100)
    G42.add_constraint(x <= 100)
    ha.set_guard(("Q4", "Q2"), G42)

    ha.add_edge(from_location="Q2", to_location="Q5")
    G25 = ppl.NNC_Polyhedron(2, 'universe')
    G25.add_constraint(x >= -100)
    G25.add_constraint(x <= 100)
    ha.set_guard(("Q2", "Q5"), G25)

    ha.add_edge(from_location="Q5", to_location="Q2")
    G52 = ppl.NNC_Polyhedron(2, 'universe')
    G52.add_constraint(x >= -100)
    G52.add_constraint(x <= 100)
    ha.set_guard(("Q5", "Q2"), G52)

    return ha
