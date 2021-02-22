import pytest

from hysynth.utils.hybrid_system import HybridSystemBoundaryCollections
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


@pytest.fixture()
def hs_loc_edge_3var():

    # initialize
    hs = HybridSystemBoundaryCollections("Mock-Tester", [get_var(1), get_var(2), get_var(3)])

    # add locations
    hs.add_location("Q1")
    hs.add_location("Q2")
    hs.add_location("Q3")

    # add edges
    hs.add_edge("Q1", "Q1")
    hs.add_edge("Q1", "Q2")
    hs.add_edge("Q1", "Q3")

    return hs


def test_adding_invalid_flows_invalid_type(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_flow("Q1", ["I", "B"])


def test_adding_invalid_guards_invalid_type(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_guard(("Q1", "Q2"), ["I", "B"])


def test_adding_invalid_guards_non_match_variables(hs_loc_edge_3var):
    with pytest.raises(ValueError):
        hs_loc_edge_3var.set_guard(("Q1", "Q2"), {get_var(1): None, get_var(3): None})


def test_adding_invalid_invariants_invalid_type(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_invariant("Q1", ["I", "B"])


def test_adding_invalid_invariants_non_match_variables(hs_loc_edge_3var):
    with pytest.raises(ValueError):
        hs_loc_edge_3var.set_invariant("Q1", {get_var(1): None, get_var(3): None})
