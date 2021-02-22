import pytest

from hysynth.utils.hybrid_system.hybrid_system_collections import Boundary, BoundaryCollection, MutableMapping


def test_boundary_collection_mutable_mapping_subclass():
    assert issubclass(BoundaryCollection, MutableMapping)


@pytest.fixture()
def three_boundaries():
    boundary_dict = {"a": Boundary(20, -20),
                     "b": Boundary(10, -10),
                     "c": Boundary(50, -50),
                     }

    return boundary_dict


@pytest.fixture()
def three_boundaries_tuples():
    boundary_dict = {"a": (20, -20),
                     "b": (10, -10),
                     "c": (50, -50),
                     }

    return boundary_dict


def test_boundary_col_creation(three_boundaries):
    b_col = BoundaryCollection(three_boundaries)
    assert 3 == len(b_col.keys())
    assert set(b_col.keys()) == set(three_boundaries.keys())


def test_creation_with_tuples(three_boundaries_tuples):
    b_col = BoundaryCollection(three_boundaries_tuples)
    assert 3 == len(b_col.keys())
    assert set(b_col.keys()) == set(three_boundaries_tuples.keys())


def test_tuple_dict_creation_equivalence(three_boundaries,
                                         three_boundaries_tuples):

    b_col = BoundaryCollection(three_boundaries)
    b_col_tpl = BoundaryCollection(three_boundaries_tuples)

    for key, item in b_col.items():
        assert b_col_tpl[key] == item

    assert b_col == b_col_tpl


def test_creation_errors():
    not_a_dict = ["a", "b", "c"]

    with pytest.raises(TypeError):
        _ = BoundaryCollection(not_a_dict)

    mixed_dict_wrong = {"a": (20, 10),
                        "b": Boundary(50, -50),
                        "c": ["a", "not", "good"]}

    with pytest.raises(TypeError):
        _ = BoundaryCollection(mixed_dict_wrong)


@pytest.fixture()
def bound_col(three_boundaries):
    return BoundaryCollection(three_boundaries)


def test_boundary_collection_mutability(bound_col, three_boundaries):

    assert bound_col["a"] == three_boundaries["a"]

    new_boundary = Boundary(100, -100)
    bound_col["a"] = new_boundary

    assert bound_col["a"] == new_boundary

    tpl = (20, 10)
    new_boundary1 = Boundary(*tpl)
    bound_col["b"] = tpl

    assert bound_col["b"] == new_boundary1


def test_b_coll_no_addition(bound_col):

    new_boundary = Boundary(100, -100)

    with pytest.raises(KeyError):
        bound_col["x"] = new_boundary


def test_b_coll_no_deletion(bound_col):

    with pytest.raises(NotImplementedError):
        del bound_col["x"]


def test_b_coll_mutability_type_error(bound_col):

    with pytest.raises(TypeError):
        bound_col["a"] = "Funny type"


def test_b_coll_get_key_error(bound_col):

    with pytest.raises(KeyError):
        _ = bound_col["x"]


def test_get_dimension(bound_col):
    assert 3 == bound_col.dim


def test_prints_and_reprs(bound_col):
    assert str(bound_col)
    assert repr(bound_col)