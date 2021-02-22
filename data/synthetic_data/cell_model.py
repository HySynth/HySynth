import ppl

from hysynth.utils.hybrid_system import HybridSystemPolyhedral

def cell_model_ha(delta=0.1):
    """ approximation of the automaton from Fig. 5 in [Grosu et al. 2007] """
    ha = HybridSystemPolyhedral(name="CellModel",
                                variable_names=["var1"],
                                delta=delta)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # constants
    V_U = -75
    V_E = 45
    V_P = 35
    V_F = -5

    # locations
    ha.add_location("R")  # Resting/Stimulate
    IR = ppl.NNC_Polyhedron(2, 'universe')
    IR.add_constraint(x >= V_U - 1)
    IR.add_constraint(x <= V_U + 1)
    ha.set_invariant("R", IR)
    # ha.set_flow("R", {"var1": 0})
    ha.set_flow("R", [0.])

    ha.add_location("U")  # Upstroke
    IU = ppl.NNC_Polyhedron(2, 'universe')
    IU.add_constraint(x >= V_U - 1)
    IU.add_constraint(x <= V_E + 1)
    ha.set_invariant("U", IU)
    # ha.set_flow("U", {"var1": 130.02})
    ha.set_flow("U", [130.02])

    ha.add_location("E")  # Early Repolarization
    IE = ppl.NNC_Polyhedron(2, 'universe')
    IE.add_constraint(x >= V_P - 1)
    IE.add_constraint(x <= V_E + 1)
    ha.set_invariant("E", IE)
    # ha.set_flow("E", {"var1": -1.52})
    ha.set_flow("E", [-1.52])

    ha.add_location("P")  # Plateau
    IP = ppl.NNC_Polyhedron(2, 'universe')
    IP.add_constraint(x >= V_F - 1)
    IP.add_constraint(x <= V_P + 1)
    ha.set_invariant("P", IP)
    # ha.set_flow("P", {"var1": -0.76})
    ha.set_flow("P", [-0.76])

    ha.add_location("F")  # Final Repolarization
    IF = ppl.NNC_Polyhedron(2, 'universe')
    IF.add_constraint(x >= V_U - 1)
    IF.add_constraint(x <= V_P + 1)
    ha.set_invariant("F", IF)
    # ha.set_flow("F", {"var1": -2.13})
    ha.set_flow("F", [-2.13])

    # transitions
    ha.add_edge(from_location="R", to_location="U")
    GRU = ppl.NNC_Polyhedron(2, 'universe')
    GRU.add_constraint(x >= V_U - 1)
    GRU.add_constraint(x <= V_U + 1)
    ha.set_guard(("R", "U"), GRU)

    ha.add_edge(from_location="U", to_location="E")
    GUE = ppl.NNC_Polyhedron(2, 'universe')
    GUE.add_constraint(x >= V_E - 1)
    GUE.add_constraint(x <= V_E + 1)
    ha.set_guard(("U", "E"), GUE)

    ha.add_edge(from_location="E", to_location="P")
    GEP = ppl.NNC_Polyhedron(2, 'universe')
    GEP.add_constraint(x >= V_P - 1)
    GEP.add_constraint(x <= V_P + 1)
    ha.set_guard(("E", "P"), GEP)

    ha.add_edge(from_location="P", to_location="F")
    GPF = ppl.NNC_Polyhedron(2, 'universe')
    GPF.add_constraint(x >= V_F - 1)
    GPF.add_constraint(x <= V_F + 1)
    ha.set_guard(("P", "F"), GPF)

    ha.add_edge(from_location="F", to_location="R")
    GFR = ppl.NNC_Polyhedron(2, 'universe')
    GFR.add_constraint(x >= V_U - 1)
    GFR.add_constraint(x <= V_U + 1)
    ha.set_guard(("F", "R"), GFR)

    return ha
