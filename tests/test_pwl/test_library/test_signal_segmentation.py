import pytest
import numpy as np

from hysynth.pwl.library import segment_signal


def test_simple_segmentation_1D():
    l = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])

    segmented_first_test = segment_signal(l, [4])
    assert np.array_equal(segmented_first_test[(0, 4)], np.array([1, 2, 3, 4, 5]))
    assert np.array_equal(segmented_first_test[(4, 8)], np.array([5, 6, 7, 8, 9]))


@pytest.fixture()
def random_long_onedim_signal():
    random_long_signal = np.random.randint(0, 10, 10000)
    return random_long_signal


def test_random_long_signal_dimension_match(random_long_onedim_signal):
    segmented1 = segment_signal(random_long_onedim_signal, [10, 200, 1000, 5000, 8000])
    assert 6 == len(segmented1)
    assert [(0, 10), (10, 200), (200, 1000), (1000, 5000), (5000, 8000), (8000, 9999)] == list(segmented1.keys())


def test_random_long_signal_values_match(random_long_onedim_signal):
    segmented1 = segment_signal(random_long_onedim_signal, [10, 200, 1000, 5000, 8000])
    assert np.array_equal(segmented1[(0, 10)], random_long_onedim_signal[0:11])
    assert np.array_equal(segmented1[(10, 200)], random_long_onedim_signal[10:201])
    assert np.array_equal(segmented1[(5000, 8000)], random_long_onedim_signal[5000:8001])


def test_random_long_signal_with_one_cut(random_long_onedim_signal):
    segmented2 = segment_signal(random_long_onedim_signal, [10])
    assert 2 == len(segmented2)
    assert [(0, 10), (10, 9999)] == list(segmented2.keys())


def test_rls_segmentation_empty_input(random_long_onedim_signal):
    segmented3 = segment_signal(random_long_onedim_signal, [])
    assert 1 == len(segmented3)


def test_segmentation_delimeters_out_of_bounds_error(random_long_onedim_signal):

    # delimiter out of bounds
    with pytest.raises(ValueError) as excinfo:
        _ = segment_signal(random_long_onedim_signal, [2000000])

    assert 'Delimiters out of bounds!' in str(excinfo.value)


@pytest.fixture()
def random_long_multidim_signal():
    # multidimensional signal
    random_long_multidim_signal = np.random.randn(1000, 100)
    return random_long_multidim_signal


def test_segmentation_multidimensional_signal_dimensions(random_long_multidim_signal):

    segmented4 = segment_signal(random_long_multidim_signal, [10, 200, 500])
    assert 4 == len(segmented4)
    assert (11, 100) == segmented4[(0, 10)].shape
    assert (500, 100) == segmented4[(500, 999)].shape


def test_seg_mdim_sig_out_of_bounds_error(random_long_multidim_signal):

    # delimiter out of bounds
    with pytest.raises(ValueError) as excinfo:
        _ = segment_signal(random_long_multidim_signal, [10, 200, 500, 2000])

    assert 'Delimiters out of bounds!' in str(excinfo.value)


def test_seg_mdim_sig_values(random_long_multidim_signal):
    segmented4 = segment_signal(random_long_multidim_signal, [10, 200, 500])

    assert np.array_equal(random_long_multidim_signal[0:11, ...], segmented4[(0, 10)])
    assert np.array_equal(random_long_multidim_signal[10:201, ...], segmented4[(10, 200)])
    assert np.array_equal(random_long_multidim_signal[500:, ...], segmented4[(500, 999)])

