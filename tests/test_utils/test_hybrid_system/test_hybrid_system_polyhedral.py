import pytest

from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


@pytest.fixture()
def example_hs():
    hs = HybridSystemPolyhedral("Tester", get_var(1))

    # have two locations and edges between
    hs.add_location("Q1")
    hs.add_location("Q2")

    hs.add_edge("Q1", "Q2")
    hs.add_edge("Q2", "Q1")

    # now add two flows
    hs.set_flow("Q1",[1])
    hs.set_flow("Q2", [-1])

    x1 = get_var(1)
    hs.set_invariant("Q1", {x1: -1})
    hs.set_invariant("Q2", {x1: -1})


def test_printing():
    pass
