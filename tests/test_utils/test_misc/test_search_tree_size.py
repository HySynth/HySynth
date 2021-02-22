import pytest

from hysynth.utils import max_search_tree_nodes, max_search_tree_nodes_explicit


def test_search_tree_size():
    assert max_search_tree_nodes(n_modes=2, n_pieces=0) == 0 == max_search_tree_nodes_explicit(n_modes=2, n_pieces=0)
    assert max_search_tree_nodes(n_modes=2, n_pieces=1) == 3 == max_search_tree_nodes_explicit(n_modes=2, n_pieces=1)
    assert max_search_tree_nodes(n_modes=2, n_pieces=2) == 13 == max_search_tree_nodes_explicit(n_modes=2, n_pieces=2)
    assert max_search_tree_nodes(n_modes=2, n_pieces=3) == 50 == max_search_tree_nodes_explicit(n_modes=2, n_pieces=3)
    assert max_search_tree_nodes(n_modes=3, n_pieces=1) == 4 == max_search_tree_nodes_explicit(n_modes=3, n_pieces=1)
    assert max_search_tree_nodes(n_modes=3, n_pieces=2) == 21 == max_search_tree_nodes_explicit(n_modes=3, n_pieces=2)


if __name__ == "__main__":
    test_search_tree_size()
