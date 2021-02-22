import pytest

from hysynth.pwl.library import float2int


def test_float2int():
    floats = [1., -1., 2.]
    res1 = float2int(floats)
    res2 = float2int(floats, return_lcm=True)
    assert res1 == res2[0] == [1, -1, 2] and res2[1] == 1

    floats = [1.5, -1.5, 2.3]
    res1 = float2int(floats)
    res2 = float2int(floats, return_lcm=True)
    assert res1 == res2[0] == [15, -15, 23] and res2[1] == 10
