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


def test_adding_guards(hs_loc_edge_1var, hs_loc_edge_3var):
    guard = {get_var(1): None}
    hs_loc_edge_1var.set_guard(("Q1", "Q2"), guard)

    assert 3 == len(hs_loc_edge_1var.guards)
    assert 1 == len(hs_loc_edge_1var.guards[("Q1", "Q2")])

    guard3D = {get_var(1): None,
               get_var(2): None,
               get_var(3): None}

    hs_loc_edge_3var.set_guard(("Q1", "Q2"), guard3D)
    assert 3 == len(hs_loc_edge_3var.guards)
    assert 3 == len(hs_loc_edge_3var.guards[("Q1", "Q2")])


def test_adding_invalid_guards_name_not_string(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_guard(1234, None)


def test_adding_invalid_guards_location_invalid(hs_loc_edge_3var):
    with pytest.raises(ValueError):
        hs_loc_edge_3var.set_guard(("Q1", "QX"), None)


def test_adding_invalid_guard_ID_invalid_type(hs_loc_edge_3var):
    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_guard(1231234, dict())

    with pytest.raises(TypeError):
        hs_loc_edge_3var.set_guard(("Q1", "Q2", "QX"), dict())


@pytest.fixture()
def hs_with_guards(hs_loc_edge_3var):
    guard3D = {get_var(1): None,
               get_var(2): None,
               get_var(3): None}

    hs_loc_edge_3var.set_guard(("Q1", "Q2"), guard3D)

    return hs_loc_edge_3var


def test_getting_guards(hs_with_guards):
    inv = hs_with_guards.get_guard(("Q1", "Q2"))
    assert isinstance(inv, dict)
    assert set(inv.keys()) == set(hs_with_guards.variables)


def test_getting_invalid_guards_type_error(hs_with_guards):
    with pytest.raises(TypeError):
        _ = hs_with_guards.get_guard(1234)


def test_getting_invalid_guards_non_existing(hs_with_guards):
    with pytest.raises(ValueError):
        _ = hs_with_guards.get_guard(("Q1", "QX"))


def test_removing_guards(hs_with_guards):
    hs_with_guards.remove_guard(("Q1", "Q2"))

    with pytest.raises(ValueError):
        _ = hs_with_guards.get_guard(("Q1", "Q2"))


def test_removing_invalid_guards_type_error(hs_with_guards):
    with pytest.raises(TypeError):
        _ = hs_with_guards.remove_guard(1234)


def test_removing_invalid_guards_non_existing(hs_with_guards):
    with pytest.raises(ValueError):
        _ = hs_with_guards.remove_guard(("Q1", "QX"))


