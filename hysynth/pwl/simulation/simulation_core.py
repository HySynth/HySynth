""" This module contains the functions required to simulate hybrid automata - generate traces """
import random
import numpy as np
import ppl

from hysynth.pwl import library as lib
from hysynth.utils.hybrid_system import HybridSystemPolyhedral

DEFAULT_TIME = 5.


def generate_pwl_from_ha(number_of_transitions,
                         hybrid_automaton,
                         time_bound=DEFAULT_TIME,
                         starting_positions=False):
    """ This function generates a list of tuples (points) of the PWL generated by the hybrid automaton """

    if not isinstance(hybrid_automaton, HybridSystemPolyhedral):
        raise TypeError("hybrid automaton must be of the Hybrid System class")

        # resulting list of points
    generated_pwl = list()

    if starting_positions is False:

        # select a location first
        starting_location = random.choice(hybrid_automaton.locations)
        start_inv = hybrid_automaton.get_invariant(starting_location)

        # get first point
        curr_point = sample_poly(start_inv)

    elif isinstance(starting_positions, dict) and all([key in hybrid_automaton.locations
                                                       for key in starting_positions.keys()]):
        starting_location = random.choice(list(starting_positions.keys()))
        start_inv = starting_positions[starting_location]

        if isinstance(start_inv, list):
            curr_point_list = [0.]
            for constraints_in_dimension in start_inv:
                if isinstance(constraints_in_dimension, tuple) and len(constraints_in_dimension) == 2:
                    point = random.uniform(*constraints_in_dimension)
                else:
                    point = constraints_in_dimension
                curr_point_list.append(point)
            curr_point = tuple(curr_point_list)

        elif isinstance(start_inv, ppl.NNC_Polyhedron):
            curr_point = sample_poly(start_inv)

        else:
            raise ValueError("The argument starting_positions must be a "
                             "dictionary of points or polyhedra for locations")

    else:
        raise ValueError("The argument starting_positions must be a "
                         "dictionary of correct locations!")

    # set the current location
    curr_location = starting_location

    # add into the list
    generated_pwl.append(curr_point)

    while len(generated_pwl) - 1 < number_of_transitions:

        # construct tube with initial point, flow and delta
        current_ray = construct_ray(current_point=curr_point,
                                    current_location=curr_location,
                                    hybrid_automaton=hybrid_automaton)

        # intersect with all other location guards
        transitioning_locations = hybrid_automaton.find_outgoing_edges(curr_location)
        other_guards = [(tr_loc, hybrid_automaton.get_guard((curr_location, tr_loc))) for tr_loc in
                        transitioning_locations]

        # break if no transitions exist
        if not len(other_guards) > 0:
            break

        non_empty_transitions = intersect_guards(current_ray, other_guards)

        # break if no enabled guard regions exist
        if not len(non_empty_transitions) > 0:
            break

        # choose a transition
        chosen_transition = random.choice(non_empty_transitions)
        curr_location, curr_next_poly = chosen_transition

        # bound the intersected poly
        next_vertices = lib.get_vertices(curr_next_poly)
        if len(next_vertices) == 1 or (abs(next_vertices[-1][0] - next_vertices[0][0]) > time_bound):
            curr_next_poly = bound_ray_time(curr_next_poly, time_bound=time_bound)

        curr_point = sample_poly(curr_next_poly)

        # add into the list
        generated_pwl.append(curr_point)

    # handle the last point
    last_invariant = hybrid_automaton.get_invariant(curr_location)
    last_ray = construct_ray(current_point=curr_point,
                             current_location=curr_location,
                             hybrid_automaton=hybrid_automaton)

    bounded_ray = bound_final_ray(ray=last_ray, invariant=last_invariant, time_bound=time_bound)

    if not bounded_ray.is_empty():
        last_point = sample_poly(bounded_ray)
        generated_pwl.append(last_point)

    return generated_pwl


def generate_pwl_from_ha_with_time_horizon(hybrid_automaton, time_horizon,
                                           time_bound=DEFAULT_TIME, starting_positions=False):

    """ This function generates a list of tuples (points) of the PWL generated by the hybrid automaton
        until the time horizon is reached

    """

    if not isinstance(hybrid_automaton, HybridSystemPolyhedral):
        raise TypeError("hybrid automaton must be of the Hybrid System class")

    if not isinstance(time_horizon, (int, float)):
        raise TypeError("time_horizon must be a numeric type")

        # resulting list of points
    generated_pwl = list()

    if starting_positions is False:

        # select a location first
        starting_location = random.choice(hybrid_automaton.locations)
        start_inv = hybrid_automaton.get_invariant(starting_location)

        # get first point
        curr_point = sample_poly(start_inv)

    elif isinstance(starting_positions, dict) and all([key in hybrid_automaton.locations
                                                       for key in starting_positions.keys()]):
        starting_location = random.choice(list(starting_positions.keys()))
        start_inv = starting_positions[starting_location]

        if isinstance(start_inv, list):
            curr_point_list = [0.]
            for constraints_in_dimension in start_inv:
                if isinstance(constraints_in_dimension, tuple) and len(constraints_in_dimension) == 2:
                    curr_point_i = random.uniform(*constraints_in_dimension)
                else:
                    curr_point_i = constraints_in_dimension
                curr_point_list.append(curr_point_i)
            curr_point = tuple(curr_point_list)

        elif isinstance(start_inv, ppl.NNC_Polyhedron):
            curr_point = sample_poly(start_inv)

        else:
            raise ValueError("The argument starting_positions must be a "
                             "dictionary of points or polyhedra for locations")

    else:
        raise ValueError("The argument starting_positions must be a "
                         "dictionary of correct locations!")

    # set the current location
    curr_location = starting_location

    # add into the list
    generated_pwl.append(curr_point)

    # time horizon flag
    time_horizon_reached = False

    while time_horizon_reached is False:

        # import matplotlib.pyplot as plt
        # x, y = zip(*generated_pwl)
        # plt.plot(x, y)
        # plt.show()

        # construct tube with initial point, flow and delta
        current_ray = construct_ray(current_point=curr_point,
                                    current_location=curr_location,
                                    hybrid_automaton=hybrid_automaton)

        current_ray = intersect_poly(current_ray, hybrid_automaton.get_invariant(curr_location))

        prev_point = generated_pwl[-1]
        new_time_bound = time_horizon - prev_point[0]
        current_ray = bound_ray_time(current_ray, time_bound=new_time_bound)

        if np.isclose(new_time_bound, 0.0):
            break

        # intersect with all other location guards
        transitioning_locations = hybrid_automaton.find_outgoing_edges(curr_location)
        other_guards = [(tr_loc, hybrid_automaton.get_guard((curr_location, tr_loc)))
                        for tr_loc in transitioning_locations]

        # break if no transitions exist
        if not len(other_guards) > 0:
            break

        non_empty_transitions = intersect_guards(current_ray, other_guards)

        # break if no enabled guard regions exist
        if not len(non_empty_transitions) > 0:
            break

        acceptable_transitions = list()

        next_vertices = lib.get_vertices(current_ray)
        over_horizon_vx = [vx[0] >= time_horizon for vx in next_vertices]
        if any(over_horizon_vx):

            last_point = max(next_vertices, key=lambda x: x[0])
            generated_pwl.append(last_point)
            return generated_pwl
            # acceptable_transitions.append(None)

        # for each possible transitions figure out if it is within the time horizon
        # acceptable_transitions = list()
        for trans_loc, transition_poly in non_empty_transitions:

            # get the vertices
            next_vertices = lib.get_vertices(transition_poly)

            # get a time bounded ray
            if len(next_vertices) == 1:
                bounded_poly = bound_ray_time(transition_poly, time_bound=time_bound)
                next_vertices = lib.get_vertices(bounded_poly)
                transition_poly = bounded_poly

            # check how many are over the horizon
            over_horizon_vx = [vx[0] > time_horizon for vx in next_vertices]

            # if one but not all
            if any(over_horizon_vx) and not all(over_horizon_vx):
                prev_point = min(next_vertices, key=lambda x: x[0])
                new_time_bound = time_horizon - prev_point[0]

                if np.isclose(new_time_bound, 0.0):
                    continue

                bound_trans_poly = bound_ray_time(transition_poly, time_bound=new_time_bound)

                if not bound_trans_poly.is_empty():
                    break
                    # acceptable_transitions.append((trans_loc, bound_trans_poly))

                else:
                    continue

            elif all(over_horizon_vx):
                raise RuntimeError("Should never happen!")

            else:
                acceptable_transitions.append((trans_loc, transition_poly))

        if not len(acceptable_transitions) > 0:
            break

        # choose a transition
        chosen_transition = random.choice(acceptable_transitions)

        if chosen_transition is not None:
            curr_location, curr_next_poly = chosen_transition
            curr_point = sample_poly(curr_next_poly)
            generated_pwl.append(curr_point)
        else:
            break

    # handle the last point
    prev_point = generated_pwl[-1]
    new_time_bound = time_horizon - prev_point[0]

    if not np.isclose(new_time_bound, 0.0):
        last_vertices = lib.get_vertices(current_ray)
        last_point = max(last_vertices, key=lambda x: x[0])
        generated_pwl.append(last_point)

    return generated_pwl


def sample_poly(polyhedron):
    """ Uniformly get a sample point in a polyhedron """
    vertices_list = lib.get_vertices(polyhedron)
    return sample_point_from_vertices(vertices_list=vertices_list)


def sample_point_from_vertices(vertices_list):
    """ Gets a point within vertices from given vertex list, extracted for testability """

    if not len(vertices_list) > 1:
        raise ValueError("There must be at least two vertices!")

    num_v = len(vertices_list)
    random_lambdas = np.random.random_sample((num_v,))
    lambda_sum = np.sum(random_lambdas)

    normalized_lambdas = np.divide(random_lambdas, lambda_sum)

    point_in_poly = np.matmul(np.array(vertices_list).T, normalized_lambdas)

    return tuple(point_in_poly)


def construct_ray(current_point, current_location, hybrid_automaton):
    """ Construct a flow ray given an initial point, location and hybrid automaton """

    if not isinstance(hybrid_automaton, HybridSystemPolyhedral):
        raise TypeError("hybrid automaton, must be a HybridSystemPolyhedral class")

    point, lcm = lib.float2int(current_point, return_lcm=True)
    ray_coefficients = [1.]
    ray_coefficients.extend(hybrid_automaton.get_flow(current_location))
    ray = lib.float2int(ray_coefficients)

    poly = ppl.Generator_System(ppl.point(ppl.Linear_Expression(point, 0), lcm))
    poly.insert(ppl.ray(ppl.Linear_Expression(ray, 0)))

    return poly


def bound_ray_time(ray, time_bound):
    """ Bounds the ray based on time_bound """

    temp_ray = ppl.NNC_Polyhedron(ray)

    vertices = lib.get_vertices(temp_ray)
    if len(vertices) == 1:
        time = vertices[0][0]

    elif len(vertices) == 2:
        if vertices[0][0] <= vertices[1][0]:
            time = vertices[0][0]
        else:
            time = vertices[1][0]

    else:
        raise ValueError("Expected one or two vertices!")

    time_linear_expr = lib.integer_time_constraint(temp_ray.space_dimension(), time + time_bound)
    temp_ray.add_constraint(time_linear_expr <= 0)

    return temp_ray


def bound_final_ray(ray, invariant, time_bound):
    """ This function bounds the final ray of the execution based on time-bound and the invariant """

    time_bound_ray = bound_ray_time(ray=ray, time_bound=time_bound)

    return intersect_poly(time_bound_ray, invariant)


def intersect_guards(curr_tube, guards_list):
    """ Given a tube and a list of guards_list output all the non-empty intersections """

    # returned list
    non_empty_guards = list()

    for to_loc, guard_poly in guards_list:

        intersected_poly = intersect_poly(curr_tube, guard_poly)

        if not intersected_poly.is_empty():
            non_empty_guards.append((to_loc, intersected_poly))

    return non_empty_guards


def intersect_poly(poly1, poly2):
    """ This intersects two polyhedra """

    first_poly = ppl.NNC_Polyhedron(poly1)
    second_poly = ppl.NNC_Polyhedron(poly2)

    first_poly.intersection_assign(second_poly)

    return ppl.NNC_Polyhedron(first_poly)


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")
