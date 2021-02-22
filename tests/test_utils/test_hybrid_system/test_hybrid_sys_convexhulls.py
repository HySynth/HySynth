import pytest
import numpy as np
from scipy.spatial import ConvexHull

from hysynth.utils.hybrid_system import HybridSystemConvexHull
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


def test_instantiation_check():
    with pytest.raises(ValueError):
        _ = HybridSystemConvexHull("Test", [get_var(1)])


@pytest.fixture()
def mock_hs():
    hs = HybridSystemConvexHull("Test", [get_var(1), get_var(2)])

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
def mock_conv_hull():
    # create the random cloud
    n_points = 500
    n_dim = 5
    cloud = np.random.rand(n_points, n_dim)

    # create the convex hull
    hull = ConvexHull(cloud, "Qx")
    return hull


def test_adding_convex_hull_invariant(mock_hs, mock_conv_hull):
    mock_hs.set_invariant("Q1", mock_conv_hull)


def test_adding_invalid_invariant(mock_hs):
    with pytest.raises(TypeError):
        mock_hs.set_invariant("Random!")


def test_adding_convex_hull_guard(mock_hs, mock_conv_hull):
    mock_hs.set_guard(("Q1", "Q1"), mock_conv_hull)


def test_adding_invalid_guard(mock_hs):
    with pytest.raises(TypeError):
        mock_hs.set_guard("Random!")
