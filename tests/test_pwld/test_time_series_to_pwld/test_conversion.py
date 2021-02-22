import pytest

from hysynth.pwld.julia_bridge.library import load_julia_libraries, reset_seed, time_series2pwld_function


def time_series_1():
    return [(0.0, 1.0, 0.0),
            (1.0, -1.0, 0.0),
            (2.0, 1.0, 0.0),
            (3.0, -1.0, 0.0),
            (4.0, 1.0, 0.0),
            (5.0, -1.0, 0.0),
            (6.0, 1.0, 0.0),
            (7.0, -1.0, 0.0),
            (8.0, 1.0, 0.0),
            (9.0, -1.0, 0.0),
            (10.0, 1.0, 0.0)]


def test_conversion(time_series, error):
    log = 1
    dyn, x0, l = time_series2pwld_function(time_series, error, log=log)
    print("dyn:", dyn)
    print("x0:", x0)
    assert True


if __name__ == "__main__":
    load_julia_libraries(log=True)
    reset_seed(1234)

    test_conversion(time_series=time_series_1(), error=0.01)
