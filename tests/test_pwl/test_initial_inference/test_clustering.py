import pytest
import pandas as pd

from hysynth.pwl.initial_inference.lib import *
from hysynth.pwl.initial_inference.single_inference import *


def test_get_slope():
    origin = (0, 0)

    around_origin = [(1, 0),
                     (1, 1),
                     (0, 1),
                     (-1, 1),
                     (-1, 0),
                     (-1, -1),
                     (0, -1),
                     (1, -1),
                     ]

    special = (1, 2)

    # positive known
    assert [1] == get_slopes(origin, around_origin[1])
    assert [0] == get_slopes(origin, around_origin[0])
    assert [2] == get_slopes(origin, special)

    # negative known
    assert [-1] == get_slopes(origin, around_origin[-1])

    # infinity?
    with pytest.raises(ValueError):
        _ = get_slopes(origin, around_origin[2])

    # backward slopes
    with pytest.raises(ValueError):
        _ = get_slopes(origin, around_origin[3])


def test_get_slope_multidim():
    origin = (0, 0, 0, 0)

    v1 = (1, 1, 0, 0)
    v2 = (1, 0, 1, 0)
    v3 = (1, 0, 0, 1)
    v4 = (1, 1, 1, 1)

    assert [1., 0., 0.] == get_slopes(origin, v1)
    assert [0., 1., 0.] == get_slopes(origin, v2)
    assert [0., 0., 1.] == get_slopes(origin, v3)
    assert [1., 1., 1.] == get_slopes(origin, v4)


@pytest.fixture()
def pwl_short_simple_path():
    return [(0, 0), (5, 10), (10, 0), (15, 0), (20, 10), (25, 0), (30, 0), (35, 10), (40, 0), (45, 0)]


@pytest.fixture()
def pwl_pieces_short_path(pwl_short_simple_path):
    return list(zip(pwl_short_simple_path[0:-1], pwl_short_simple_path[1:]))


def test_get_pwl_pieces_slopes_df(pwl_pieces_short_path):
    pwl_single_piece = [((0, 0), (1, 2))]

    slopes_single_df = pd.DataFrame(get_pwl_slopes(pwl_pieces_list=pwl_single_piece))

    assert isinstance(slopes_single_df, pd.DataFrame)
    assert 1 == slopes_single_df.shape[0]
    assert [2.0] == slopes_single_df[0].values[0]

    slopes_df = pd.DataFrame(get_pwl_slopes(pwl_pieces_list=pwl_pieces_short_path))

    assert isinstance(slopes_df, pd.DataFrame)
    assert 9 == slopes_df.shape[0]
    assert {2.0, -2.0, 0} == set(np.unique(slopes_df[0].values).tolist())


@pytest.fixture()
def pwl_short_simple_path_ndim():
    return [(0, 0, 0), (1, 1, 0), (2, 0, 1), (3, 1, 0), (4, 0, 0), (5, 1, 0), (6, 0, 1), (7, 1, 0), (8, 0, 0)]


@pytest.fixture()
def pwl_pieces_short_path_ndim(pwl_short_simple_path_ndim):
    return list(zip(pwl_short_simple_path_ndim[0:-1], pwl_short_simple_path_ndim[1:]))


def test_get_pwl_pieces_slopes_df_ndim(pwl_pieces_short_path_ndim):

    slopes_df = pd.DataFrame(get_pwl_slopes(pwl_pieces_list=pwl_pieces_short_path_ndim))

    clusters_dict = meanshift_clustering(segment_flows_df=slopes_df,
                                         epsilon=0.5)

    assert isinstance(clusters_dict, dict)

    # must match
    expected = [[0, 4], [1, 5], [2, 6], [3, 7]]
    assert len(clusters_dict) == len(clusters_dict)
    for v in clusters_dict.values():
        assert v in expected


def test_meanshift_clustering_example(pwl_pieces_short_path):
    slopes_df = pd.DataFrame(get_pwl_slopes(pwl_pieces_list=pwl_pieces_short_path))

    clusters_dict = meanshift_clustering(segment_flows_df=slopes_df,
                                         epsilon=0.5)

    assert isinstance(clusters_dict, dict)

    # must match
    expected = [[0, 3, 6], [1, 4, 7], [2, 5, 8]]
    assert len(clusters_dict) == len(clusters_dict)
    for v in clusters_dict.values():
        assert v in expected
