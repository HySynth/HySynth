from queue import PriorityQueue
from copy import deepcopy

from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwld.julia_bridge.library import square, is_similar_flow, is_captured,\
    successor_set, issubset, polytope_hull, compute_reach_tube_hull
from hysynth.utils.hybrid_system.library import construct_location_name
from hysynth.utils import max_search_tree_nodes


# TODO remove print statements
# priority queue with entries (m, d, l, t, c, i, p, H, R) represent a path in the search tree; the entries stand for:
# - m: total number of modifications (= c + t + l)
# - d: -1 * path depth (negative for preferring large values in the priority queue)
# - l: number of added locations
# - t: number of added transitions
# - c: number of constraint modifications
# - i: item index (used for tie breaking such that further entries do not require an order relation)
# - p: path (sequence of locations)
# - H: hybrid automaton corresponding to the corresponding path
# - R: overapproximation of last reachable set
# - G: set of modified guards
class PathQueue(object):
    def __init__(self):
        self.queue = PriorityQueue()
        self.elems = 0
        self.elems_total = 0
        self.elems_explored = -1  # root node should not be counted

    def __str__(self):
        return "path queue with {:d} elements: {}".format(self.elems, list(self.queue.queue))

    def put(self, item):
        self.queue.put((
            item.l_mods,
            item.t_mods,
            item.c_mods,
            item.path_depth,
            self.elems_total,
            item.path,
            item.automaton,
            item.reach,
            item.modified_guards
        ))
        self.elems += 1
        self.elems_total += 1
        # print("putting item to the queue: {}".format(item.longstr()))
        # print(str(self))

    def pop(self):
        self.elems -= 1
        self.elems_explored += 1
        l_mods, t_mods, c_mods, path_depth, index, path, automaton, reach, modified_guards = self.queue.get()
        # print("popping queue item {:d}".format(index))
        return PathQueueItem(path_depth=path_depth, l_mods=l_mods, t_mods=t_mods, c_mods=c_mods, path=path,
                             automaton=automaton, reach=reach, modified_guards=modified_guards)

    def isempty(self):
        return self.elems <= 0


class PathQueueItem(object):
    def __init__(self, path_depth, l_mods, t_mods, c_mods, path, automaton, reach, modified_guards):
        self.path_depth = path_depth
        self.l_mods = l_mods
        self.t_mods = t_mods
        self.c_mods = c_mods
        self.path = path
        self.automaton = automaton
        self.reach = reach
        self.modified_guards = modified_guards

    def __str__(self):
        return "<depth {}, L {}, T {}, C {}, P {}>".format(
            -self.path_depth, self.l_mods, self.t_mods, self.c_mods, self.path)

    def longstr(self):
        return "<depth {}, L {}, T {}, C {}, G {}, P {}, R {}, H {}>".format(
            -self.path_depth, self.l_mods, self.t_mods, self.c_mods, self.modified_guards, self.path, self.reach,
            self.automaton)


# general idea:
# - find a first location to dwell
# - in a loop, find the next location to jump to and then dwell there
def adapt_automaton_to_pwld_function(pwld_function, x0, hybrid_automaton: HybridSystemPolyhedral, tube_radius,
                                     data_index, n_discrete_steps, refinement_distance, reachability_time_step,
                                     statistics=None, log=False):
    if not pwld_function:
        # a function with no pieces does not require any modifications
        return hybrid_automaton

    # compute time durations from time points
    pwld_function_time_points = []
    pwld_function_time_durations = []
    t = 0.0
    for i, (dyn, time_point) in enumerate(pwld_function):
        pwld_function_time_points.append((dyn, time_point))
        pwld_function_time_durations.append((dyn, time_point - t))
        t = time_point
    if log:
        print("--- considering function of length", len(pwld_function), ":", pwld_function)

    path_length = len(pwld_function)

    # compute tube at switching points
    Qs = []
    x = x0
    for i in range(path_length + 1):
        if i > 0:
            dyn, time = pwld_function_time_durations[i-1]
            x = dyn.successor(time, x)
        Q = square(x, tube_radius)
        if log > 3:
            print("Q{:d}: {}".format(i, Q))
        Qs.append(Q)

    # initialize queue with empty path
    path_queue = PathQueue()
    first_item = PathQueueItem(path_depth=0, l_mods=0, t_mods=0, c_mods=0, path=[],
                               automaton=hybrid_automaton, reach=Qs[0], modified_guards=set())
    path_queue.put(first_item)

    candidates_without_definite_answers = []
    if log:
        print("---starting loop")
    while True:
        if path_queue.isempty():
            assert candidates_without_definite_answers,\
                "By construction, we should always find a suitable path."
            if log:
                print("Due to approximation errors, we could not find any definite answer. We will now choose "
                      "the modification that is guaranteed to succeed theoretically.")
                print("Old automaton: {}".format(hybrid_automaton))
                for item in candidates_without_definite_answers:
                    if item.l_mods == path_length:
                        print("New automaton: {}".format(item.automaton))
                        if statistics is not None:
                            report_tree_nodes_to_statistics(statistics=statistics, path_queue=path_queue,
                                                            hybrid_automaton=hybrid_automaton,
                                                            pwld_function=pwld_function)
                        return item.automaton

        if log > 1:
            print("--loop iteration")
        if log > 3:
            print(str(path_queue))
        item = path_queue.pop()
        if log > 2:
            print("-processing next item:", item)
        old_path = item.path
        old_automaton = item.automaton
        if len(old_path) == path_length:
            if log > 1:
                print("--------------------- new membership test ---------------------")
            if log > 2:
                print(old_path)
            answer, is_definite_answer = is_captured(pwld_function_time_points, x0, old_path, old_automaton,
                                                     tube_radius, n_discrete_steps, refinement_distance, log=log > 0)
            if answer:
                # found best path (i.e., with fewest/smallest automaton modifications)
                if log > 3:
                    print("accepted automaton:", old_automaton)
                if statistics is not None:
                    report_tree_nodes_to_statistics(statistics=statistics, path_queue=path_queue,
                                                    hybrid_automaton=hybrid_automaton, pwld_function=pwld_function)
                return old_automaton
            elif not is_definite_answer:
                candidates_without_definite_answers.append(item)
            continue  # this path in the search tree did not work out
        path_depth = item.path_depth - 1  # note the '-' because these numbers are (additively) inverted
        P0 = item.reach
        Q0 = Qs[-item.path_depth]  # tube at beginning of the piece
        Q1 = Qs[-path_depth]  # tube at end of the piece
        dyn, time = pwld_function_time_durations[-item.path_depth]

        if not old_path:
            # no location yet
            prev_location = None
            succ_locations = []
        else:
            # further locations
            prev_location = item.path[-1]
            succ_locations = old_automaton.find_outgoing_edges(prev_location)

        # paths with existing locations
        l_mods = item.l_mods
        if log > 1:
            print("currently in location:", prev_location)
        for location in old_automaton.locations:
            if log > 1:
                print("consider successor:", location)

            dyn2 = old_automaton.get_flow(location)
            if log > 3:
                print("B:", dyn2)
            is_similar, P1 = is_similar_flow(P0, dyn2, Q1, time, return_set=True)
            if log > 3:
                print("is_similar:", is_similar)
            if not is_similar:
                continue

            c_mods = item.c_mods
            path = deepcopy(old_path)
            path.append(location)
            new_automaton = item.automaton.deepcopy()

            reach_tube_hull = compute_reach_tube_hull(dyn2, P0, time, reachability_time_step)
            old_invariant = old_automaton.get_invariant(location)
            if change_invariant(old_invariant, reach_tube_hull):
                c_mods += 1
                new_invariant = polytope_hull(old_invariant, reach_tube_hull)
                new_automaton.set_invariant(location, new_invariant)

            edge = (prev_location, location)
            modified_guards = item.modified_guards
            if not old_path:
                # first location, no transition
                t_mods = 0
            elif location in succ_locations:
                # use existing transition
                t_mods = item.t_mods

                old_guard = new_automaton.get_guard(edge)
                if change_guard(old_guard, Q0):
                    new_guard = polytope_hull(old_guard, Q0)
                    if log > 3:
                        print("setting guard for {} from {} to {}".format(edge, old_guard, new_guard))
                        print("Q0: {}, loc: {}, path: {}".format(Q0, prev_location, path))
                    new_automaton.set_guard(edge_tuple=edge, guard=new_guard)
                    if edge not in modified_guards:
                        c_mods += 1
                        modified_guards = modified_guards.copy()
                        modified_guards.add(edge)
            else:
                # add new transition
                t_mods = item.t_mods + 1
                new_automaton.add_edge(from_location=prev_location, to_location=location)
                if log > 3:
                    print("adding transition {} with guard {}".format(edge, Q1))
                new_automaton.set_guard(edge_tuple=edge, guard=Q0)

            new_item = PathQueueItem(path_depth=path_depth, l_mods=l_mods, t_mods=t_mods, c_mods=c_mods, path=path,
                                     automaton=new_automaton, reach=P1, modified_guards=modified_guards)
            if log > 2:
                print("-resulting item:", new_item)
            path_queue.put(new_item)

        # path with new location
        # print("dyn2 = dyn:", dyn)
        l_mods = item.l_mods + 1
        c_mods = item.c_mods
        modified_guards = item.modified_guards
        new_automaton = old_automaton.deepcopy()
        location = construct_location_name(len(old_automaton.locations))
        new_automaton.add_location(location)
        new_automaton.set_flow(location, dyn, rounding=False, skip_rounding=True)
        new_invariant = compute_reach_tube_hull(dyn, P0, time, reachability_time_step)
        new_automaton.set_invariant(location, new_invariant)
        P1 = successor_set(dyn, time, P0)  # TODO instead we could use Q1 which is also an overapproximation of P1 ∩ Q1
        if not old_path:
            # first location, no transition
            t_mods = item.t_mods
        else:
            # add a transition
            t_mods = item.t_mods + 1
            new_automaton.add_edge(from_location=prev_location, to_location=location)
            # print("adding transition {} with guard {}".format((prev_location, location), Q1))
            new_automaton.set_guard(edge_tuple=(prev_location, location), guard=Q0)
        path = deepcopy(old_path)
        path.append(location)
        new_item = PathQueueItem(path_depth=path_depth, l_mods=l_mods, t_mods=t_mods, c_mods=c_mods, path=path,
                                 automaton=new_automaton, reach=P1, modified_guards=modified_guards)
        # print("-resulting item:", new_item)
        path_queue.put(new_item)


def report_tree_nodes_to_statistics(statistics, path_queue, hybrid_automaton, pwld_function):
    key_nodes = "list #tree nodes"
    key_locations = "list #locations"
    key_pieces = "list #pieces"
    # key_nodes_max = "list #tree nodes max"
    n_locations = len(hybrid_automaton.locations)
    n_pieces = len(pwld_function)
    # n_nodes_max = max_search_tree_nodes(n_modes=n_locations, n_pieces=n_pieces)
    nodes_list = statistics.get_delta_entry(key=key_nodes)
    if nodes_list is None:
        nodes_list = [path_queue.elems_explored]
        locations_list = [n_locations]
        pieces_list = [n_pieces]
        # nodes_max_list = [n_nodes_max]
        statistics.add(key=key_nodes, value=nodes_list)
        statistics.add(key=key_locations, value=locations_list)
        statistics.add(key=key_pieces, value=pieces_list)
        # statistics.add(key=key_nodes_max, value=nodes_max_list)
    else:
        nodes_list.append(path_queue.elems_explored)
        locations_list = statistics.get_delta_entry(key=key_locations)
        locations_list.append(n_locations)
        pieces_list = statistics.get_delta_entry(key=key_pieces)
        pieces_list.append(n_pieces)
        # nodes_max_list = statistics.get_delta_entry(key=key_nodes_max)
        # nodes_max_list.append(n_nodes_max)


def change_invariant(old_invariant, reach_tube_hull):
    return not issubset(reach_tube_hull, old_invariant)


def change_guard(old_guard, Q1):
    return not issubset(Q1, old_guard)
