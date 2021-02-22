import math

import pytest
import numpy as np

from data.synthetic_data.automata_library import two_mode_p1_m1_ha
from hysynth.pwl.simulation import generate_pwl_dataset, generate_timeseries_dataset
from hysynth.pwl.simulation.dataset_generation import save_dataset, load_dataset


@pytest.fixture()
def example_pwl_dataset():
    ha_in = two_mode_p1_m1_ha()
    return generate_pwl_dataset(hybrid_automaton=ha_in, n_iterations=5, max_jumps=10)


def test_timeseries_sampling(example_pwl_dataset):

    ts_dataset1 = generate_timeseries_dataset(pwl_dataset=example_pwl_dataset, sampling_frequency=1)
    ts_dataset05 = generate_timeseries_dataset(pwl_dataset=example_pwl_dataset, sampling_frequency=0.5)
    ts_dataset01 = generate_timeseries_dataset(pwl_dataset=example_pwl_dataset, sampling_frequency=0.1)

    assert ts_dataset1.shape == (5, 41)
    assert ts_dataset05.shape == (5, 82)
    assert ts_dataset01.shape == (5, 410)


@pytest.fixture()
def example_ts_dataset(example_pwl_dataset):
    return generate_timeseries_dataset(pwl_dataset=example_pwl_dataset, sampling_frequency=0.1)


@pytest.fixture(scope='session')
def save_file_lol(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('data_lol.json')
    return fn


def test_saving_loading_pwl(example_pwl_dataset, save_file_lol):

    # test saving
    save_dataset(example_pwl_dataset, save_file_lol)

    loaded_dset = load_dataset(save_file_lol, "lol")

    # must be is close, cuz floats!
    assert all([math.isclose(orig_val[0], loaded_var[0]) and math.isclose(orig_val[1], loaded_var[1])
                for orig_row, loaded_row in zip(example_pwl_dataset, loaded_dset)
                for orig_val, loaded_var in zip(orig_row, loaded_row)])


@pytest.fixture(scope='session')
def save_file_df(tmpdir_factory):
    fn = tmpdir_factory.mktemp('data').join('data_df.json')
    return fn


def test_saving_loading_df(example_ts_dataset, save_file_df):

    # test saving
    save_dataset(example_ts_dataset, save_file_df)

    loaded_dset = load_dataset(save_file_df, "df")

    assert np.all(np.isclose(example_ts_dataset.columns.values,
                             loaded_dset.columns.values))

    for (idx1, row1), (idx2, row2)  in zip(example_ts_dataset.iterrows(),
                                           loaded_dset.iterrows()):
        row1 = row1.dropna()
        row2 = row2.dropna()  # NaN evaluates to false

        assert np.isclose(row1.values, row2.values).all()
