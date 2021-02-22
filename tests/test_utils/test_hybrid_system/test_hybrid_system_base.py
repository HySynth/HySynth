import pytest

from hysynth.utils.hybrid_system.hybrid_system_base import HybridSystemBase, HybridSystemABC
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


def test_require_subclassing():
    with pytest.raises(TypeError):
        _ = HybridSystemABC("No workey!")


def test_subclassing():
    instance = HybridSystemBase("All is good!", [get_var(1)])

    assert isinstance(instance, HybridSystemBase)
    assert issubclass(HybridSystemBase, HybridSystemABC)
    assert 1 == instance.dim


def test_instantiation_checks():
    with pytest.raises(TypeError) as exc:
        _ = HybridSystemBase(123, [get_var(1)])
    assert str(exc.value) == "Name of the Hybrid System must be a string"

    with pytest.raises(TypeError) as exc:
        _ = HybridSystemBase("Bal", "x1")
    assert str(exc.value) == "Variable names must be a list!"

    with pytest.raises(TypeError) as exc:
        _ = HybridSystemBase("Fun!", ["x1", 123])
    assert str(exc.value) == "Variable names must all be strings!"

    with pytest.raises(ValueError) as exc:
        _ = HybridSystemBase("test", ["x1", "x2", "x3", "x1"])
    assert str(exc.value) == "Variable names must be unique, no repeats!"


@pytest.fixture()
def fake_hs_class_instance():
    return HybridSystemBase("Im a Mock", [get_var(1)])


def test_add_location(fake_hs_class_instance):
    fake_hs_class_instance.add_location("Q1")
    fake_hs_class_instance.add_location("Q2")
    fake_hs_class_instance.add_location("Q3")

    assert isinstance(fake_hs_class_instance.locations, list)
    assert 3 == len(fake_hs_class_instance.locations)


def test_add_same_location(fake_hs_class_instance):
    fake_hs_class_instance.add_location("Q1")
    with pytest.raises(ValueError):
        fake_hs_class_instance.add_location("Q1")

    assert isinstance(fake_hs_class_instance.locations, list)
    assert 1 == len(fake_hs_class_instance.locations)


def test_add_location_error(fake_hs_class_instance):
    with pytest.raises(TypeError):
        fake_hs_class_instance.add_location(1)


def test_remove_location(fake_hs_class_instance):
    fake_hs_class_instance.add_location("Q1")
    fake_hs_class_instance.add_location("Q2")
    fake_hs_class_instance.add_location("Q3")

    assert isinstance(fake_hs_class_instance.locations, list)
    assert 3 == len(fake_hs_class_instance.locations)

    fake_hs_class_instance.remove_location("Q1")
    assert 2 == len(fake_hs_class_instance.locations)


def test_remove_location_invalid(fake_hs_class_instance):
    fake_hs_class_instance.add_location("Q1")
    with pytest.raises(TypeError):
        fake_hs_class_instance.remove_location(123)


def test_remove_location_key_error(fake_hs_class_instance):
    fake_hs_class_instance.add_location("Q1")
    with pytest.raises(KeyError):
        fake_hs_class_instance.remove_location("QX")


@pytest.fixture()
def hs_with_locations(fake_hs_class_instance):
    fake_hs_class_instance.add_location("Q1")
    fake_hs_class_instance.add_location("Q2")
    fake_hs_class_instance.add_location("Q3")
    return fake_hs_class_instance


def test_add_self_edge(hs_with_locations):
    hs_with_locations.add_edge("Q1", "Q1")

    assert isinstance(hs_with_locations.edges, list)
    assert 1 == len(hs_with_locations.edges)


def test_add_edges(hs_with_locations):
    hs_with_locations.add_edge("Q1", "Q1")
    hs_with_locations.add_edge("Q1", "Q2")
    hs_with_locations.add_edge("Q1", "Q3")

    assert 3 == len(hs_with_locations.edges)


def test_add_same_edges(hs_with_locations):
    hs_with_locations.add_edge("Q1", "Q2")
    hs_with_locations.add_edge("Q1", "Q2")

    assert 1 == len(hs_with_locations.edges)


def test_add_both_dir_edges(hs_with_locations):
    hs_with_locations.add_edge("Q1", "Q2")
    hs_with_locations.add_edge("Q2", "Q1")

    assert 2 == len(hs_with_locations.edges)


def test_add_invalid_edges_error(hs_with_locations):
    with pytest.raises(TypeError):
        hs_with_locations.add_edge(123, "Q2")

    with pytest.raises(TypeError):
        hs_with_locations.add_edge("Q1", 123)

    with pytest.raises(TypeError):
        hs_with_locations.add_edge(123, 1234)


def test_remove_edges(hs_with_locations):
    hs_with_locations.add_edge("Q1", "Q2")
    hs_with_locations.add_edge("Q2", "Q1")
    assert 2 == len(hs_with_locations.edges)

    hs_with_locations.remove_edge("Q1", "Q2")
    assert 1 == len(hs_with_locations.edges)


def test_add_invalid_edge(hs_with_locations):
    with pytest.raises(KeyError):
        hs_with_locations.add_edge("QX", "QY")


def test_remove_invalid_edge(hs_with_locations):
    with pytest.raises(KeyError):
        hs_with_locations.remove_edge("QX", "QY")


def test_remove_invalid_type_edge(hs_with_locations):
    with pytest.raises(TypeError):
        hs_with_locations.remove_edge(123, "QY")

    with pytest.raises(TypeError):
        hs_with_locations.remove_edge("QX", 123)

    with pytest.raises(TypeError):
        hs_with_locations.remove_edge(52345, 52345)


@pytest.fixture()
def hs_with_edges(hs_with_locations):
    hs_with_locations.add_edge("Q1", "Q1")
    hs_with_locations.add_edge("Q1", "Q2")
    hs_with_locations.add_edge("Q1", "Q3")

    return hs_with_locations


def test_hs_printing(hs_with_edges):
    assert str(hs_with_edges)


def test_accepts_path_good(hs_with_edges):
    path1 = ["Q1", "Q1"]
    path2 = ["Q1", "Q1", "Q1", "Q1", "Q1", "Q1", "Q1", "Q1"]
    path3 = ["Q1", "Q1", "Q1", "Q2"]
    path4 = ["Q1", "Q1", "Q1", "Q3"]
    path5 = ["Q1", "Q3"]
    path6 = ["Q1", "Q2"]

    assert hs_with_edges.accepts_path(path1)
    assert hs_with_edges.accepts_path(path2)
    assert hs_with_edges.accepts_path(path3)
    assert hs_with_edges.accepts_path(path4)
    assert hs_with_edges.accepts_path(path5)
    assert hs_with_edges.accepts_path(path6)


def test_accepts_path_invalid_path(hs_with_edges):
    path1 = ["Q3", "Q1"]
    path2 = ["Q1", "Q1", "Q3", "Q1", "Q1", "Q1", "Q1", "Q1"]
    path3 = ["Q1", "Q2", "Q1", "Q2"]
    path4 = ["Q2", "Q1", "Q1", "Q3"]
    path5 = ["Q1", "Q3", "Q1"]
    path6 = ["Q1", "Q2", "Q1"]

    assert not hs_with_edges.accepts_path(path1)
    assert not hs_with_edges.accepts_path(path2)
    assert not hs_with_edges.accepts_path(path3)
    assert not hs_with_edges.accepts_path(path4)
    assert not hs_with_edges.accepts_path(path5)
    assert not hs_with_edges.accepts_path(path6)


def test_accepts_path_invalid_locations(hs_with_edges):
    path1 = ["Q3", "QX"]
    path2 = ["Q1", "Q1", "Q3", "QX", "Q1", "Q1", "Q1", "Q1"]
    path3 = ["Q1", "QX", "Q1", "Q2"]
    path4 = ["QX", "Q1", "Q1", "Q3"]
    path5 = ["Q1", "QX", "Q1"]
    path6 = ["Q1", "Q2", "QX"]

    with pytest.raises(ValueError):
        assert hs_with_edges.accepts_path(path1)

    with pytest.raises(ValueError):
        assert hs_with_edges.accepts_path(path2)

    with pytest.raises(ValueError):
        assert hs_with_edges.accepts_path(path3)

    with pytest.raises(ValueError):
        assert hs_with_edges.accepts_path(path4)

    with pytest.raises(ValueError):
        assert hs_with_edges.accepts_path(path5)

    with pytest.raises(ValueError):
        assert hs_with_edges.accepts_path(path6)


def test_accepts_path_single_element(hs_with_edges):
    path1 = ["Q3"]
    assert hs_with_edges.accepts_path(path1)


def test_accepts_path_invalid_types(hs_with_edges):
    path1 = 123
    path2 = [123, "Q1"]

    with pytest.raises(TypeError):
        assert hs_with_edges.accepts_path(path1)

    with pytest.raises(TypeError):
        assert hs_with_edges.accepts_path(path2)




