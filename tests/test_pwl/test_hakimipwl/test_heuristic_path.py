import pytest

from hysynth.pwl.hakimi_pwl.unroll_hakimi import heuristic_dfs


@pytest.fixture()
def path_dict():
    return {0: {"Q1": 0.5,
                "Q2": 0.5,
                "Q3": 0.1,
                "Q4": 0.5,},

            1: {"Q1": 0.1,
                "Q2": 0.5,
                "Q3": 0.5,
                "Q4": 0.5, },

            2: {"Q1": 0.5,
                "Q2": 0.1,
                "Q3": 0.5,
                "Q4": 0.5, },

            3: {"Q1": 0.5,
                "Q2": 0.5,
                "Q3": 0.5,
                "Q4": 0.1, },

            4: {"Q1": 0.5,
                "Q2": 0.1,
                "Q3": 0.5,
                "Q4": 0.5, },
            }


@pytest.fixture()
def path_dict_backtrack():
    return {0: {"Q1": 0.5,
                "Q2": 0.5,
                "Q3": 0.1,
                "Q4": 0.5,},

            1: {"Q1": 0.1,
                "Q2": 0.5,
                "Q3": 0.5,
                "Q4": 0.5, },

            2: {"Q1": 0.5,
                "Q2": 0.1,
                "Q3": 2,
                "Q4": 1, },

            3: {"Q1": 0.5,
                "Q2": 0.01,
                "Q3": 1,
                "Q4": 0.1, },

            4: {"Q1": 0.5,
                "Q2": 0.1,
                "Q3": 0.5,
                "Q4": 0.5, },
            }


@pytest.fixture()
def edges_all():
    return {("Q1", "Q2") : True,
          ("Q1", "Q3"): True,
          ("Q1", "Q4"): True,

          ("Q2", "Q1"): True,
          ("Q2", "Q3"): True,
          ("Q2", "Q4"): True,

          ("Q3", "Q1"): True,
          ("Q3", "Q2"): True,
          ("Q3", "Q4"): True,

          ("Q4", "Q1"): True,
          ("Q4", "Q2"): True,
          ("Q4", "Q3"): True,
          }


@pytest.fixture()
def edges_sparse():
    return {("Q1", "Q2"): True,
            ("Q1", "Q3"): True,
            ("Q1", "Q4"): True,

            ("Q2", "Q1"): False,
            ("Q2", "Q3"): False,
            ("Q2", "Q4"): False,

            ("Q3", "Q1"): True,
            ("Q3", "Q2"): False,
            ("Q3", "Q4"): False,

            ("Q4", "Q1"): False,
            ("Q4", "Q2"): True,
            ("Q4", "Q3"): True,
            }


@pytest.fixture()
def has_edge_full(edges_all):
    def _func(location_from, location_to):
        return edges_all[(location_from, location_to)]

    return _func


@pytest.fixture()
def has_edge_sparse(edges_sparse):
    def _func(location_from, location_to):
        return edges_sparse[(location_from, location_to)]

    return _func


def test_depth_first_simple(path_dict, has_edge_full):
    best_path, _ = heuristic_dfs(path_dict=path_dict, has_edge_function=has_edge_full)
    assert isinstance(best_path, list)
    assert best_path == ['Q3', 'Q1', 'Q2', 'Q4', 'Q2']


def test_depth_first_backtracking(path_dict_backtrack, has_edge_sparse):
    best_path, _ = heuristic_dfs(path_dict=path_dict_backtrack, has_edge_function=has_edge_sparse)
    assert isinstance(best_path, list)
    assert best_path == ['Q3', 'Q1', 'Q4', 'Q3', 'Q1']
