import pytest

from hysynth import ha_adaptation_from_data_pwl
from data.synthetic_data.automata_library import two_mode_p1_m1_ha
from hysynth.pwl.simulation.dataset_generation import generate_pwl_dataset, generate_timeseries_dataset


@pytest.fixture()
def pwl_dataset_1():
    ha_in = two_mode_p1_m1_ha()

    pwl_dset = generate_pwl_dataset(hybrid_automaton=ha_in, n_iterations=5, max_jumps=10)

    return pwl_dset


@pytest.fixture()
def ts_dataset_1(pwl_dataset_1):
    ts_dataset = generate_timeseries_dataset(pwl_dataset=pwl_dataset_1, sampling_frequency=0.5)
    return ts_dataset


@pytest.fixture()
def pwl_dataset_short():
    ha_in = two_mode_p1_m1_ha()

    pwl_dset = generate_pwl_dataset(hybrid_automaton=ha_in, n_iterations=5, max_jumps=10)

    return pwl_dset


def test_ha_adaptation_1(ts_dataset_1):
    real_ha = two_mode_p1_m1_ha()
    real_ha._delta = 0.5  # only a hack allowed for testing

    result_ha = ha_adaptation_from_data_pwl(data=ts_dataset_1, hybrid_automaton=real_ha, pwl_epsilon=0.25)

    assert len(result_ha.locations) >= 2
    assert ('Q1', 'Q2') in result_ha.edges
    assert ('Q2', 'Q1') in result_ha.edges
    assert result_ha.get_flow("Q1") == [1]
    assert result_ha.get_flow("Q2") == [-1]
