import pytest
import data.real_data.preprocess as prep

from hysynth import ha_synthesis_from_data_pwl


@pytest.fixture()
def time_series_dataset():

    filename1 = "data/real_data/datasets/ekg_data/ekg_1.csv"
    filename2 = "data/real_data/datasets/ekg_data/ekg_2.csv"
    filename3 = "data/real_data/datasets/ekg_data/ekg_3.csv"

    f1 = prep.data2array(filename1, 2)
    f2 = prep.data2array(filename2, 2)
    f3 = prep.data2array(filename3, 2)

    return [f1, f2, f3]


def test_sequence_of_ekg(time_series_dataset):
    ha = ha_synthesis_from_data_pwl(timeseries_data=time_series_dataset,
                                    delta_ha=0.25,
                                    pwl_epsilon=0.0,
                                    clustering_bandwidth=False)

    print(ha)

    assert True
