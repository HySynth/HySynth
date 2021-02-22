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


def test_adding_invariants(hs_loc_edge_1var, hs_loc_edge_3var):
    invariant = {get_var(1): None}
    hs_loc_edge_1var.set_invariant("Q1", invariant)

    assert 3 == len(hs_loc_edge_1var.invariants)
    assert 1 == len(hs_loc_edge_1var.invariants["Q1"])

    invariant3D = {get_var(1): None,
                   get_var(2): None,
                   get_var(3): None}

    hs_loc_edge_3var.set_invariant("Q1", invariant3D)
    assert 3 == len(hs_loc_edge_3var.invariants)
    assert 3 == len(hs_loc_edge_3var.invariants["Q1"])


def test_adding_invalid_invariants_name_not_string(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_invariant(1234, None)


def test_adding_invalid_invariants_location_invalid(hs_loc_edge_3var):
    with pytest.raises(ValueError):
        hs_loc_edge_3var.set_invariant("NONLOC", None)


@pytest.fixture()
def hs_with_invariants(hs_loc_edge_3var):
    invariant3D = {get_var(1): None,
                   get_var(2): None,
                   get_var(3): None}

    hs_loc_edge_3var.set_invariant("Q1", invariant3D)

    return hs_loc_edge_3var


def test_getting_invariants(hs_with_invariants):
    inv = hs_with_invariants.get_invariant("Q1")
    assert isinstance(inv, dict)
    assert set(inv.keys()) == set(hs_with_invariants.variables)


def test_getting_invalid_invariants_type_error(hs_with_invariants):
    with pytest.raises(TypeError):
        _ = hs_with_invariants.get_invariant(1234)


def test_getting_invalid_invariants_non_existing(hs_with_invariants):
    with pytest.raises(ValueError):
        _ = hs_with_invariants.get_invariant("QX")


def test_removing_invariants(hs_with_invariants):
    hs_with_invariants.remove_invariant("Q1")

    with pytest.raises(ValueError):
        _ = hs_with_invariants.get_invariant("Q1")


def test_removing_invalid_invariants_type_error(hs_with_invariants):
    with pytest.raises(TypeError):
        _ = hs_with_invariants.remove_invariant(1234)


def test_removing_invalid_invariants_non_existing(hs_with_invariants):
    with pytest.raises(ValueError):
        _ = hs_with_invariants.remove_invariant("QX")


