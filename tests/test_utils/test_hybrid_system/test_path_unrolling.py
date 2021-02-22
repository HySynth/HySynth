import pytest
import networkx as nx

from hysynth.utils.hybrid_system import hybrid_system_base as hsb


@pytest.fixture()
def simple_graph():
    g = nx.DiGraph()

    g.add_nodes_from(["A", "B", "C", "D"])

    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("C", "D")
    g.add_edge("D", "B")

    return g


def test_find_paths_correct_length(simple_graph):
    paths1 = hsb.get_all_k_paths(simple_graph, 3)

    for path in paths1:
        assert isinstance(path, list)
        assert 3+1 == len(path)

    paths2 = hsb.get_all_k_paths(simple_graph, 0)

    assert 4 == len(paths2)
    for path in paths2:
        assert isinstance(path, list)
        assert 1 == len(path)

    paths3 = hsb.get_all_k_paths(simple_graph, 10)

    for path in paths3:
        assert isinstance(path, list)
        assert 10 + 1 == len(path)


@pytest.fixture()
def graph_with_side_sink():
    g = nx.DiGraph()

    g.add_nodes_from(["A", "B", "C"])

    g.add_edge("A", "B")
    g.add_edge("B", "C")

    return g


def test_find_paths_with_side_sink(graph_with_side_sink):
    paths1 = hsb.get_all_k_paths(graph_with_side_sink, 2)

    # check if "C" is in the paths (should be)
    assert ["A", "B", "C"] == paths1[0]

    # should raise error
    with pytest.raises(ValueError):
        _ = hsb.get_all_k_paths(graph_with_side_sink, 3)

    with pytest.raises(ValueError):
        _ = hsb.get_all_k_paths(graph_with_side_sink, 10)
