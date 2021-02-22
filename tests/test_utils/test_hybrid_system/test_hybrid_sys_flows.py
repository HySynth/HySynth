import pytest

from hysynth.utils.hybrid_system import HybridSystemBase
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


@pytest.fixture()
def hs_loc_edge_1var():

    # initialize
    hs = HybridSystemBase("Mock-Tester", [get_var(1)])

    # add locations
    hs.add_location("Q1")
    hs.add_location("Q2")
    hs.add_location("Q3")

    # add edges
    hs.add_edge("Q1", "Q1")
    hs.add_edge("Q1", "Q2")
    hs.add_edge("Q1", "Q3")

    return hs


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


def test_adding_flows(hs_loc_edge_1var, hs_loc_edge_3var):
    flow = {get_var(1): None}
    hs_loc_edge_1var.set_flow("Q1", flow)

    assert 3 == len(hs_loc_edge_1var.flows)
    assert 1 == len(hs_loc_edge_1var.flows["Q1"])

    hs_loc_edge_3var.set_flow("Q1", [None, None, None])
    assert 3 == len(hs_loc_edge_3var.flows)
    assert 3 == len(hs_loc_edge_3var.flows["Q1"])


def test_adding_invalid_flows_name_not_string(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_flow(1234, None)


def test_adding_invalid_flows_location_invalid(hs_loc_edge_3var):
    with pytest.raises(ValueError):
        hs_loc_edge_3var.set_flow("NONLOC", None)


@pytest.fixture()
def hs_with_flows(hs_loc_edge_3var):
    hs_loc_edge_3var.set_flow("Q1", [None, None, None])

    return hs_loc_edge_3var


def test_getting_flows(hs_with_flows):
    flow = hs_with_flows.get_flow("Q1")
    assert flow == [None, None, None]


def test_getting_invalid_flows_type_error(hs_with_flows):
    with pytest.raises(TypeError):
        _ = hs_with_flows.get_flow(1234)


def test_getting_invalid_flows_non_existing(hs_with_flows):
    with pytest.raises(ValueError):
        _ = hs_with_flows.get_flow("QX")


def test_removing_flows(hs_with_flows):
    hs_with_flows.remove_flow("Q1")

    with pytest.raises(ValueError):
        _ = hs_with_flows.get_flow("Q1")


def test_removing_invalid_flows_type_error(hs_with_flows):
    with pytest.raises(TypeError):
        _ = hs_with_flows.remove_flow(1234)


def test_removing_invalid_flows_non_existing(hs_with_flows):
    with pytest.raises(ValueError):
        _ = hs_with_flows.remove_flow("QX")