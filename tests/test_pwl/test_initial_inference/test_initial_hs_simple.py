import pytest

from hysynth.pwl.initial_inference import infer_hybrid_system_polyhedral_pwl


@pytest.fixture()
def pwl_short_simple_path():
    return [(0, 0), (5, 10), (10, 0), (15, 0), (20, 10), (25, 0), (30, 0), (35, 10), (40, 0), (45, 0)]


@pytest.fixture()
def pwl_path_with_variable_slopes():
    return [(0, 0), (5, 10), (10, 0), (15, 0), (20, 10), (25, 0), (30, 0), (35, 10), (40, 0), (45, 0)]


# @pytest.mark.skip("This test needs to be adapted for high-dimensional clustering.")
def test_initialhs_with_short_simple_path(pwl_short_simple_path):
    # we choose use the deltas and the meanshift epsilon arbitrary here as it is just a test

    initial_hs = infer_hybrid_system_polyhedral_pwl(pwl_points_list=pwl_short_simple_path,
                                                    delta_ha=1.0,
                                                    delta_fh=0.5,
                                                    epsilon_meanshift=0.5,
                                                    only_consider_first_piece=False)

    # should have 3 locations
    assert 3 == len(initial_hs.locations)

    # should contain only one visible variable, but 2 parma variables
    assert {"x1"} == initial_hs.variables

    # the flows should match
    expected_flows = [2.0, -2.0, 0.0]
    flow2name = {}
    assert len(initial_hs.flows) == len(expected_flows)
    for name, v in initial_hs.flows.items():
        for v2 in v:
            assert v2 in expected_flows
            flow2name[v2] = name

    # the edges should be [('Q0', 'Q1'), ('Q1', 'Q2'), ('Q2', 'Q0')]
    Q0 = flow2name[2.0]
    Q1 = flow2name[-2.0]
    Q2 = flow2name[0.0]
    expected_transitions = [(Q0, Q1), (Q1, Q2), (Q2, Q0)]
    assert len(initial_hs.edges) == len(expected_transitions)
    for t in initial_hs.edges:
        assert t in expected_transitions


@pytest.fixture()
def pwl_path_with_variable_slopes():
    return [(0, 0), (5, 10), (10, 0), (15, 0), (20, 10), (25, 0), (30, 0), (35, 10), (40, 0), (45, 0)]


def test_initialhs_clustering_disabled(pwl_short_simple_path):
    # we choose use the deltas and the meanshift epsilon arbitrary here as it is just a test

    initial_hs = infer_hybrid_system_polyhedral_pwl(pwl_points_list=pwl_short_simple_path,
                                                    delta_ha=1.0,
                                                    delta_fh=0.5,
                                                    epsilon_meanshift=False,
                                                    only_consider_first_piece=False)

    assert len(initial_hs.locations) == 3
    assert initial_hs.flows == {'Q0' : [2.0], 'Q1' : [-2.0], 'Q2' : [0.0]}
    assert initial_hs.edges == [('Q0', 'Q1'), ('Q1', 'Q2'), ('Q2', 'Q0')]


def test_initialhs_clustering_default(pwl_short_simple_path):
    # we choose use the deltas and the meanshift epsilon arbitrary here as it is just a test

    initial_hs = infer_hybrid_system_polyhedral_pwl(pwl_points_list=pwl_short_simple_path,
                                                    delta_ha=1.0,
                                                    delta_fh=0.5,
                                                    only_consider_first_piece=False)

    assert len(initial_hs.locations) == 3
    assert initial_hs.flows == {'Q0' : [2.0], 'Q1' : [-2.0], 'Q2' : [0.0]}
    assert initial_hs.edges == [('Q0', 'Q1'), ('Q1', 'Q2'), ('Q2', 'Q0')]




