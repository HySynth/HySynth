from random import choice

from hysynth.utils import argmins_list
from hysynth.utils.sets import SetRep
from hysynth.pwld.julia_bridge.library import load_julia_libraries, sample_from_set, contains, set2julia


def sample_trajectory_pwld(hybrid_automaton, path_length, max_dwell_time, time_step, min_dwell_time=None,
                           initial_condition=None, max_perturbation=0.0, avoid_self_loops=False,
                           prefer_new_locations=False, log=False):
    if isinstance(max_dwell_time, list):
        if len(max_dwell_time) < path_length:
            raise (ValueError("max_dwell_time needs at least length {:d}".format(path_length)))
    elif max_dwell_time < time_step:
        raise(ValueError("max_dwell_time < time_step"))

    load_julia_libraries()

    if initial_condition is None:
        # default initial condition: mapping 'loc ↦ None' for every location loc
        initial_condition = dict.fromkeys(hybrid_automaton.locations)

    if not isinstance(max_dwell_time, list):
        max_dwell_time = [max_dwell_time for _ in range(path_length)]
    if min_dwell_time is None:
        min_dwell_time = 0.0
    if not isinstance(min_dwell_time, list):
        min_dwell_time = [min_dwell_time for _ in range(path_length)]

    if prefer_new_locations:
        location_visits = {loc: 0 for loc in hybrid_automaton.locations}

    while True:
        # choose initial location and state
        initial_location, initial_set = choice(list(initial_condition.items()))
        if log > 1:
            print("initial: {}, {}".format(initial_location, initial_set))
        if initial_set is None:
            # default initial set: location's invariant
            initial_set = hybrid_automaton.get_invariant(initial_location)
        if isinstance(initial_set, SetRep):
            initial_set = set2julia(initial_set)
        x0 = sample_from_set(initial_set)
        if log > 1:
            print("x0: {}".format(x0))

        location_old = initial_location
        point_old = x0
        t_old = 0.0
        path = []

        i = -1
        while len(path) < path_length - 1:
            i += 1
            successors = hybrid_automaton.find_outgoing_edges(location_old)
            active = dict()
            point = point_old
            dyn = hybrid_automaton.get_flow(location_old)
            dyn = dyn.perturb(max_perturbation)
            invariant = set2julia(hybrid_automaton.get_invariant(location_old))
            t = t_old + time_step  # we require a non-zero dwell time
            t_max = t_old + max_dwell_time[i]
            t_min = t_old + min_dwell_time[i]
            while t < t_max:
                point = dyn.successor(time_step, point)
                if log > 3:
                    print("next point: {}".format(point))
                if not contains(invariant, point):
                    if log > 2:
                        print("leaving invariant: {}, point: {}".format(invariant, point))
                    break
                for location_next in successors:
                    edge = (location_old, location_next)
                    guard = set2julia(hybrid_automaton.get_guard(edge))
                    if t >= t_min and contains(guard, point):
                        if location_next in active:
                            active[location_next].append(t)
                        else:
                            active[location_next] = [t]
                t += time_step

            if not active:
                # no next transition
                if log > 1:
                    print("no next transition")
                break

            # choose a successor location and jump time
            active_locations = list(active.keys())
            if avoid_self_loops and len(active_locations) > 1 and location_old in active_locations:
                active_locations.remove(location_old)
            if prefer_new_locations:
                occurrences = [location_visits[active_loc] for active_loc in active_locations]
                min_indices = argmins_list(occurrences)
                active_locations = [active_locations[i] for i in min_indices]
            location_new = choice(active_locations)
            if prefer_new_locations:
                location_visits[location_new] = location_visits[location_new] + 1
            t_new = choice(active[location_new])
            point_new = dyn.successor(t_new - t_old, point_old)
            path.append((location_old, t_new, dyn))
            if log > 1:
                print("moving to {} at t = {} (x = {})".format(location_new, t_new, point_new))

            t_old = t_new
            point_old = point_new
            location_old = location_new

        # choose some end point in the current location
        if log > 1:
            print("done with the transitions, dwelling now")
        t = t_old + time_step  # we require a non-zero dwell time
        times = []
        point = point_old
        t_max = t_old + max_dwell_time[path_length - 1]
        t_min = t_old + min_dwell_time[path_length - 1]
        dyn = hybrid_automaton.get_flow(location_old)
        dyn = dyn.perturb(max_perturbation)
        invariant = set2julia(hybrid_automaton.get_invariant(location_old))
        if log > 2:
            print("point: {}".format(point))
            print("invariant: {}".format(invariant))
        while t < t_max:
            point = dyn.successor(time_step, point)
            if not contains(invariant, point):
                break
            if t >= t_min:
                times.append(t)
            t += time_step
        if not times:
            # reached a location where dwelling is not possible
            # print("reached a location where dwelling is not possible: {}, F: {}, I: {}, p: {}".format(
            #     location_old, A, invariant, point_old))
            if log > 1:
                print("could not dwell there, trying again")
            continue
        else:
            t_new = choice(times)
            path.append((location_old, t_new, dyn))
            if log > 1:
                print("t = {}".format(t_new))
            break

    return path, x0
