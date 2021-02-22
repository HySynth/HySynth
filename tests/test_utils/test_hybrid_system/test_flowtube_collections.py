import pytest

from hysynth.utils.hybrid_system.hybrid_system_collections import Flowtube, FlowtubeCollection, MutableMapping


def test_boundary_collection_mutable_mapping_subclass():
    assert issubclass(FlowtubeCollection, MutableMapping)


@pytest.fixture()
def three_flowtubes():
    boundary_dict = {"a": Flowtube(20, -20),
                     "b": Flowtube(10, -10),
                     "c": Flowtube(50, -50),
                     }

    return boundary_dict


@pytest.fixture()
def three_flowtube_tuples():
    boundary_dict = {"a": (20, -20),
                     "b": (10, -10),
                     "c": (50, -50),
                     }

    return boundary_dict


def test_flowtube_col_creation(three_flowtubes):
    b_col = FlowtubeCollection(three_flowtubes)
    assert 3 == len(b_col.keys())
    assert set(b_col.keys()) == set(three_flowtubes.keys())


def test_creation_with_tuples(three_flowtubes):
    b_col = FlowtubeCollection(three_flowtubes)
    assert 3 == len(b_col.keys())
    assert set(b_col.keys()) == set(three_flowtubes.keys())


def test_tuple_dict_creation_equivalence(three_flowtubes, three_flowtube_tuples):

    b_col = FlowtubeCollection(three_flowtubes)
    b_col_tpl = FlowtubeCollection(three_flowtube_tuples)

    for key, item in b_col.items():
        assert b_col_tpl[key] == item

    assert b_col == b_col_tpl


def test_creation_errors():
    not_a_dict = ["a", "b", "c"]

    with pytest.raises(TypeError):
        _ = FlowtubeCollection(not_a_dict)

    mixed_dict_wrong = {"a": (20, 10),
                        "b": Flowtube(50, -50),
                        "c": ["a", "not", "good"]}

    with pytest.raises(TypeError):
        _ = FlowtubeCollection(mixed_dict_wrong)


@pytest.fixture()
def flow_col(three_flowtubes):
    return FlowtubeCollection(three_flowtubes)


def test_flowtube_collection_mutability(flow_col, three_flowtubes):

    assert flow_col["a"] == three_flowtubes["a"]

    new_boundary = Flowtube(100, -100)
    flow_col["a"] = new_boundary

    assert flow_col["a"] == new_boundary

    tpl = (20, 10)
    new_boundary1 = Flowtube(*tpl)
    flow_col["b"] = tpl

    assert flow_col["b"] == new_boundary1


def test_f_coll_no_addition(flow_col):

    new_boundary = Flowtube(100, -100)

    with pytest.raises(KeyError):
        flow_col["x"] = new_boundary


def test_f_coll_no_deletion(flow_col):

    with pytest.raises(NotImplementedError):
        del flow_col["x"]


def test_f_coll_mutability_type_error(flow_col):

    with pytest.raises(TypeError):
        flow_col["a"] = "Funny type"


def test_f_coll_get_key_error(flow_col):

    with pytest.raises(KeyError):
        _ = flow_col["x"]


def test_get_dimension(flow_col):
    assert 3 == flow_col.dim


def test_prints_and_reprs(flow_col):
    assert str(flow_col)
    assert repr(flow_col)