import pytest

from hysynth.utils.hybrid_system import HybridSystemBase
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


@pytest.fixture()
def hs_loc_edge_3var():

    # initialize
    hs = HybridSystemBase("Mock-Tester", [get_var(1), get_var(2), get_var(3)])

    # add locations
    hs.add_location("Q1")
    hs.add_location("Q2")
    hs.add_location("Q3")

    # add edges
    hs.add_edge("Q1", "Q1")
    hs.add_edge("Q1", "Q2")
    hs.add_edge("Q1", "Q3")

    return hs


def test_copying_identity(hs_loc_edge_3var):

    first = hs_loc_edge_3var
    copied = first.copy()

    assert id(first) == id(hs_loc_edge_3var)
    assert not id(first) == id(copied)


def test_copying_contents(hs_loc_edge_3var):

    first = hs_loc_edge_3var
    copied = first.copy()

    assert first.variables == copied.variables
    assert first.locations == copied.locations
    assert first.flows == copied.flows
    assert first.guards == copied.guards
    assert first.invariants == copied.invariants
