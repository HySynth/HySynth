import pytest
import numpy as np
from scipy.spatial import ConvexHull

# what we are testing
from hysynth.pwl.library import points_in_hull, point_in_hull


@pytest.fixture
def simple_cloud_and_hull():
    cloud = np.array([[10, -10], [10, 10], [-10, 10], [-10, -10]])
    hull = ConvexHull(cloud)
    return cloud, hull


def test_simple_points_in_hull(simple_cloud_and_hull):

    cloud, hull = simple_cloud_and_hull

    sample_point1 = np.array([5, 5])
    assert point_in_hull(sample_point1, hull)

    sample_point2 = np.array([-5, 5])
    assert point_in_hull(sample_point2, hull)

    sample_point3 = np.array([5, -5])
    assert point_in_hull(sample_point3, hull)

    sample_point4 = np.array([-5, -5])
    assert point_in_hull(sample_point4, hull)


def test_simple_points_not_in_hull(simple_cloud_and_hull):

    cloud, hull = simple_cloud_and_hull

    # not in hull!
    sample_point11 = np.array([50, 50])
    assert not point_in_hull(sample_point11, hull)

    sample_point12 = np.array([-50, 50])
    assert not point_in_hull(sample_point12, hull)

    sample_point13 = np.array([50, -50])
    assert not point_in_hull(sample_point13, hull)

    sample_point14 = np.array([-50, -50])
    assert not point_in_hull(sample_point14, hull)


@pytest.fixture
def random_big_cloud_and_hull():
    # np.random.seed(999)

    # create the random cloud
    n_points = 500
    n_dim = 5
    cloud = np.random.rand(n_points, n_dim)

    # create the convex hull
    hull = ConvexHull(cloud, "Qx")

    return cloud, hull


def test_fuzzy_point_in_hull_big_scale(simple_cloud_and_hull):

    cloud, hull = simple_cloud_and_hull

    # they must all be in hull
    for _ in range(100):
        sample_point = cloud[np.random.randint(0, cloud.shape[0])]
        assert True is point_in_hull(sample_point, hull)


def test_points_in_hull(simple_cloud_and_hull):

    cloud, hull = simple_cloud_and_hull

    sample_points = [cloud[np.random.randint(0, cloud.shape[0])] for _ in range(100)]

    assert np.all(points_in_hull(sample_points, hull))
