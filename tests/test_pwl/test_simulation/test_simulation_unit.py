import random
import numpy as np

import pytest
import ppl


from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwl import simulation as sim
import hysynth.pwl.library as lib


@pytest.fixture()
def single_dim_poly_1():
    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    sdim = ppl.NNC_Polyhedron(2, 'universe')
    sdim.add_constraint(x >= 0)
    sdim.add_constraint(x <= 10)

    return sdim


@pytest.fixture()
def single_dim_poly_2():
    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    sdim = ppl.NNC_Polyhedron(2, 'universe')
    sdim.add_constraint(x >= 4)
    sdim.add_constraint(x <= 7)

    return sdim


@pytest.fixture()
def single_dim_poly_3():
    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    sdim = ppl.NNC_Polyhedron(2, 'universe')
    sdim.add_constraint(x >= 8)
    sdim.add_constraint(x <= 15)

    return sdim


@pytest.fixture()
def single_dim_poly_4():
    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    sdim = ppl.NNC_Polyhedron(2, 'universe')
    sdim.add_constraint(x >= 20)
    sdim.add_constraint(x <= 30)

    return sdim


@pytest.fixture()
def multi_dim_poly():
    pass


@pytest.fixture()
def two_mode_ha_1():
    """ Simple zig zag automaton """
    ha = HybridSystemPolyhedral(name="TwoModeTest",
                                variable_names=["var1"],
                                delta=0.5)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # add locations
    ha.add_location("Q1")
    ha.add_location("Q2")

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 10)

    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 10)

    ha.set_invariant("Q1", I1)
    ha.set_invariant("Q2", I2)

    # add flow
    ha.set_flow("Q1", {"var1": 1})
    ha.set_flow("Q2", {"var1": -1})

    # add edges
    ha.add_edge(to_location="Q1", from_location="Q2")
    ha.add_edge(to_location="Q2", from_location="Q1")

    # guards
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 5)
    G12.add_constraint(x <= 10)

    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 5)
    G21.add_constraint(x <= 10)

    ha.set_guard(("Q1", "Q2"), G12)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


@pytest.fixture()
def two_mode_ha_2():
    """ Simple zig zag automaton """
    ha = HybridSystemPolyhedral(name="TwoModeTest",
                                variable_names=["var1"],
                                delta=0.5)

    # PPL variables
    _ = ppl.Variable(0)
    x = ppl.Variable(1)

    # add locations
    ha.add_location("Q1")
    ha.add_location("Q2")

    # invariants
    I1 = ppl.NNC_Polyhedron(2, 'universe')
    I1.add_constraint(x >= 0)
    I1.add_constraint(x <= 10)

    I2 = ppl.NNC_Polyhedron(2, 'universe')
    I2.add_constraint(x >= 0)
    I2.add_constraint(x <= 10)

    ha.set_invariant("Q1", I1)
    ha.set_invariant("Q2", I2)

    # add flow
    ha.set_flow("Q1", [1])
    ha.set_flow("Q2", [-1])

    # add edges
    ha.add_edge(to_location="Q1", from_location="Q2")
    ha.add_edge(to_location="Q2", from_location="Q1")

    # guards
    G12 = ppl.NNC_Polyhedron(2, 'universe')
    G12.add_constraint(x >= 5)
    G12.add_constraint(x <= 10)

    G21 = ppl.NNC_Polyhedron(2, 'universe')
    G21.add_constraint(x >= 0)
    G21.add_constraint(x <= 5)

    ha.set_guard(("Q1", "Q2"), G12)
    ha.set_guard(("Q2", "Q1"), G21)

    return ha


def test_2mode_ha_basic_run(two_mode_ha_2):

    random.seed(1234)
    np.random.seed(1234)

    pwl_line = sim.generate_pwl_from_ha(number_of_transitions=4, hybrid_automaton=two_mode_ha_2)

    assert isinstance(pwl_line, list)
    assert all(map(lambda x: isinstance(x, tuple) and len(x) == 2, pwl_line))

    assert 6 == len(pwl_line)

    # assert [(0.0, 7.646106104272788),
    #         (5.856666835451012, 1.7894392688217755),
    #         (10.36212014468856, 6.294892578059323),
    #         (15.375111051038246, 1.2819016717096372),
    #         (21.48115445528475, 7.387945075956139)] \
    #         == pwl_line


def test_intersection_function(single_dim_poly_1, single_dim_poly_2, single_dim_poly_3):

    first_intersect = sim.simulation_core.intersect_poly(single_dim_poly_1, single_dim_poly_2)

    vert1 = lib.get_vertices(first_intersect)
    assert [(0, 4), (0, 7)] == vert1

    second_intersect = sim.simulation_core.intersect_poly(single_dim_poly_2, single_dim_poly_3)
    assert second_intersect.is_empty()

    third_intersect = sim.simulation_core.intersect_poly(single_dim_poly_1, single_dim_poly_3)

    vert3 = lib.get_vertices(third_intersect)
    assert [(0, 8), (0, 10)] == vert3


def test_multiple_guard_intersections(single_dim_poly_1, single_dim_poly_2, single_dim_poly_3, single_dim_poly_4):

    non_empty_guards = sim.simulation_core.intersect_guards(curr_tube=single_dim_poly_1,
                                                guards_list=[("Q1", single_dim_poly_2),
                                                             ("Q2", single_dim_poly_3),
                                                             ("Q3", single_dim_poly_4)])

    assert isinstance(non_empty_guards, list)
    assert 2 == len(non_empty_guards)

    assert "Q1" == non_empty_guards[0][0]
    assert "Q2" == non_empty_guards[1][0]

    vert1 = lib.get_vertices(non_empty_guards[0][1])
    vert2 = lib.get_vertices(non_empty_guards[1][1])

    assert [(0, 4), (0, 7)] == vert1
    assert [(0, 8), (0, 10)] == vert2


def test_get_vertices_from_poly():
    """ Provide vertices for poly, check if you get same back """
    pass


def test_get_point_from_vertex_list():
    """ Provide a 3d cube from which to sample  check if the samples are within range and in proper type """
    point1 = (0, 0, 0)
    point2 = (0, 10, 0)
    point3 = (10, 0, 0)
    point4 = (10, 10, 0)
    point5 = (0, 0, 10)
    point6 = (0, 10, 10)
    point7 = (10, 0, 10)
    point8 = (10, 10, 10)

    vertex_list = [point1, point2, point3, point4, point5, point6, point7, point8]

    # run a few samples
    for _ in range(0, 500):
        new_point = sim.simulation_core.sample_point_from_vertices(vertex_list)

        assert isinstance(new_point, tuple)
        assert 3 == len(new_point)

        assert 0 <= new_point[0] < 10
        assert 0 <= new_point[1] < 10
        assert 0 <= new_point[2] < 10


def test_polyhedron_sampling_1dim(single_dim_poly_1):
    point_in_poly = sim.simulation_core.sample_poly(single_dim_poly_1)

    assert isinstance(point_in_poly, tuple)
    assert 0 <= point_in_poly[0] < 10
