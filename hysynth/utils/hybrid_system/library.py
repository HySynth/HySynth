import datetime
from math import isclose


def construct_hybrid_automaton_name(name=None):
    if name is None:
        curr_datetime = datetime.datetime.now()
        name = "test_hs_{month}{day}{hour}{minute}".format(month=curr_datetime.month,
                                                           day=curr_datetime.day,
                                                           hour=curr_datetime.hour,
                                                           minute=curr_datetime.minute)
    return name


def construct_location_name(cluster_id):
    return "Q{}".format(str(cluster_id))


def construct_variable_name(index):
    return "x{}".format(str(index))


def construct_variable_names(pw_function, function_type):
    if function_type == "pwl":
        n = len(pw_function[0])
    elif function_type == "pwld":
        n = pw_function[0][0].dim() + 1
    else:
        raise ValueError("function_type is not known:", function_type)
    return [construct_variable_name(i) for i in range(1, n)]


def get_delta_fh(delta_ha, epsilon_f, allow_zero_delta=False):
    delta_fh = delta_ha - epsilon_f

    if delta_fh < 0.0:
        raise ValueError("delta_fh should never be negative!")
    if not allow_zero_delta and isclose(delta_fh, 0.0):
        raise ValueError("delta_fh should never be zero!")

    return delta_fh


def map_initial_condition(old_initial_condition, old_automaton, new_automaton):
    if old_initial_condition is None:
        return old_initial_condition

    new_initial_condition = dict()
    for (old_loc, cond) in old_initial_condition.items():
        new_loc = None
        old_flow = old_automaton.get_flow(old_loc)
        for loc in new_automaton.locations:
            flow = new_automaton.get_flow(loc)
            if old_flow == flow:
                if new_loc is None:
                    new_loc = loc
                else:
                    raise(ValueError("found multiple new locations corresponding to old location {}".format(old_loc)))
        if new_loc is None:
            raise(ValueError("could not find a new location corresponding to old location {}".format(old_loc)))
        new_initial_condition[new_loc] = cond
    return new_initial_condition
