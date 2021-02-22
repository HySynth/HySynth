""" This short module just contains the unroll hakimi convenience function """
from collections import defaultdict


def unroll_hakimi(hybrid_system, hakimi_path):

    # first get the number of transitions for the hakimi path (one less than number of nodes)
    n_hakimi_transitions = len(hakimi_path) - 2

    return hybrid_system.unroll(n_transitions=n_hakimi_transitions)


def get_heuristic_path(pwl_path, hybrid_automaton):
    path_dict = construct_paths_dict(pwl_path=pwl_path, hybrid_automaton=hybrid_automaton)
    return heuristic_dfs(path_dict=path_dict, has_edge_function=hybrid_automaton.has_edge)


def construct_paths_dict(pwl_path, hybrid_automaton):

    ha_slopes = {loc: flow for loc, flow in hybrid_automaton.flows.items()}

    slope_distance_dict = defaultdict(dict)

    for trans_idx, pwl_piece in enumerate(zip(pwl_path[:-1], pwl_path[1:])):
        pwl_piece_slope = get_slope(*pwl_piece)

        for curr_ha_loc, curr_ha_slope in ha_slopes.items():
            curr_slope_diff = [abs(pwl_piece_slope[i] - curr_ha_slope[i]) for i in range(len(pwl_piece_slope))]

            slope_distance_dict[trans_idx][curr_ha_loc] = curr_slope_diff

    return slope_distance_dict


def heuristic_dfs(path_dict, has_edge_function):

    # initialize
    path = []
    stack = _sort_candidates(path_dict[len(path)].items())
    desired_len = len(path_dict.keys())
    if desired_len == 0:
        return path, True

    while len(stack):
        next_loc = stack.pop(0)
        path.append(next_loc)

        if len(path) == desired_len:
            return path, True

        try:
            new_stack = _expand_n_sort(prev_loc=next_loc, trans_n=len(path),
                                       path_dict=path_dict, has_edge_function=has_edge_function)

        except ValueError:
            if not len(stack):
                # no path of desired length; keep the last element in the path to prevent an empty path
                return path, False

            # backtrack
            _ = path.pop()
            continue

        else:
            stack = new_stack + stack

    # no path of the desired length exists
    return path, False


def _expand_n_sort(prev_loc, trans_n, path_dict, has_edge_function):
    """ Finds possible paths and sorts by distance to original pwl piece """
    return _sort_candidates(_get_candidates(prev_loc, trans_n, path_dict, has_edge_function))


def _get_candidates(prev_loc, trans_n, path_dict, has_edge_function):

    candidates_list = [(next_location, closeness)
                       for next_location, closeness in path_dict[trans_n].items()
                       if prev_loc != next_location and has_edge_function(prev_loc, next_location)]

    if not candidates_list:
        raise ValueError("No candidates!")

    else:
        return candidates_list


def _sort_candidates(candidates):
    return [location for location, _ in sorted(candidates, key=lambda x: x[1])]


def get_slope(p1, p2):
    if p2[0] < p1[0]:
        raise ValueError("Backward slopes don't make sense in this context!")

    try:
        den = p2[0] - p1[0]
        result = [(p2[i] - p1[i]) / den for i in range(1, len(p1))]

    except ZeroDivisionError as e:
        raise ValueError("Infinite slopes don't make sense in this context!") from e

    else:
        return result
