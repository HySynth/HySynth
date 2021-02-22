import pytest
import numpy as np

from julia.api import Julia
JULIA = Julia(compiled_modules=False)
from julia import Main as jl


def test_julia():
    length = jl.length([1, 1])
    assert length == 2
    fn = jl.include("tests/test_pwld/test_julia/test_julia.jl")
    x = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64)
    fn(x)


if __name__ == "__main__":
    test_julia()
