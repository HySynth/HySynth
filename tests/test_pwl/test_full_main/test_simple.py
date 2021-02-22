import pytest

from hysynth import ha_synthesis_from_data_pwl


@pytest.fixture()
def time_series_dataset():
    f1 = [(0., 0.), (5., 5.), (10., 5.)]
    f2 = [(0., 5.), (5., 0.), (10., 0.)]
    f3 = [(0., 5.), (5., 0.), (10., 5.)]
    # f4 = [(0., 0.), (5., 5.), (10., 5.), (15., 2.5)]

    return [f1, f2, f3]


def test_sequence_of_3(time_series_dataset):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_2():
    f1 = [(0., 4.), (1., 5.), (2., 4.)]
    f2 = [(0., 2.), (3., 5.), (5.5, 2.5)]
    f3 = [(0., 3.), (2., 1.)]

    # f1 = [(0., 4.5), (0.5, 5.), (1., 4.5)]
    # f2 = [(0., 3.5), (1.25, 4.75), (4., 2.)]
    # f3 = [(0., 1.), (3.5, 4.5), (5., 3.)]

    return [f1, f2, f3]


def test_sequence_of_ds2(time_series_dataset_2):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_2,
                                    delta_ha=0.25,
                                    pwl_epsilon=False,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_3():

    f1 = [(0., 4.5), (0.5, 5.), (1., 4.5)]
    f2 = [(0., 3.5), (1.25, 4.75), (4., 2.)]
    f3 = [(0., 1.), (3.5, 4.5), (5., 3.)]

    return [f1, f2, f3]


def test_sequence_of_ds3(time_series_dataset_3):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_3,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_4():

    f1 = [(0., 4.5), (0.5, 5.), (1., 4.5)]
    f2 = [(0., 3.5), (1.25, 4.75), (4., 2.)]
    f3 = [(0., 1.), (3.5, 4.5), (5., 3.)]
    f4 = [(0., 1.), (3.5, 4.5), (5., 4.)]

    return [f1, f2, f3, f4]


def test_sequence_of_ds4(time_series_dataset_4):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_4,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_5():

    f1 = [(0., 4.5), (0.5, 5.), (1., 4.5)]
    f2 = [(0., 3.5), (1.25, 4.75), (4., 2.)]
    f3 = [(0., 1.), (3.5, 4.5), (5., 3.)]

    return [f2, f1, f3]


def test_sequence_of_ds5(time_series_dataset_5):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_5,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_6():

    f1 = [(0., 4.5), (0.5, 5.), (1., 4.5)]
    f2 = [(0., 3.5), (1.25, 4.75), (4., 2.)]
    f3 = [(0., 1.), (3.5, 4.5), (5., 3.)]

    return [f2, f3, f1]


def test_sequence_of_ds6(time_series_dataset_6):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_6,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_7():

    f1 = [(0., 0.), (1., 1.), (2., 1.)]
    f2 = [(0., 0.), (1., 1.), (2., 1.5)]

    return [f1, f2]


def test_sequence_of_ds7(time_series_dataset_7):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_7,
                                    delta_ha=0.2,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    assert True


@pytest.fixture()
def time_series_dataset_3d():
    # the third dimension is always identical to the second dimension
    f1 = [(0., 0., 0.), (5., 5., 5.), (10., 5., 5.)]
    f2 = [(0., 5., 5.), (5., 0., 0.), (10., 0., 0.)]
    f3 = [(0., 5., 5.), (5., 0., 0.), (10., 5., 5.)]

    return [f1, f2, f3]


def test_sequence_of_3_3d(time_series_dataset_3d):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset_3d,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth = False)

    assert True
