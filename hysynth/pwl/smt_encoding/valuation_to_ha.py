from hysynth.pwl.initial_inference.single_inference import infer_hybrid_system_polyhedral_pwl
from hysynth.pwl.library import merge


def get_first_index_of_symbol(valuation, symbol):
    for i, (var, val) in enumerate(valuation):
        if var[0] == symbol:
            return i
    raise ValueError('Did not find any valuation starting with symbol {0}.'.format(symbol))


def get_slopes_list(valuation, start_index, function_index):
    prefix = 'b_f{0}'.format(function_index)
    prefix_length = len(prefix)
    new_slopes_list = []
    offset = 0
    for offset, (var, val) in enumerate(valuation[start_index:]):
        if var[0:prefix_length] != prefix:
            # new function
            break
        elif var[-3:] == '_d1':
            # same function, new point
            new_slopes_list.append([val])
        else:
            # same function, same point, new dimension
            new_slopes_list[-1].append(val)
    return new_slopes_list, start_index + offset


def get_points_list(valuation, function, start_index, function_index):
    prefix = 'x_f{0}'.format(function_index)
    prefix_length = len(prefix)
    pwl_points_list = []
    k = 0
    offset = 0
    for offset, (var, val) in enumerate(valuation[start_index:]):
        if var[0:prefix_length] != prefix:
            # new function
            break
        elif var[-3:] == '_d1':
            # same function, new point
            time = function[k][0]
            pwl_points_list.append([time, val])
            k += 1
        else:
            # same function, same point, new dimension
            pwl_points_list[-1].append(val)
    # convert lists to tuple
    pwl_points_list_converted = []
    for pair_list in pwl_points_list:
        pwl_points_list_converted.append(tuple(pair_list))
    return pwl_points_list_converted, start_index + offset


def valuation_to_hybrid_automaton(functions, valuation, epsilon, bloating, hybrid_automaton=None):
    """
    Convert a valuation of the SMT formula to a new hybrid automaton
    :param functions: list of PWL functions used to create the valuation (only used to obtain the switching times, so a
           list of one-dimensional vectors with just the time points is sufficient)
    :param valuation: list of pairs '(var, val)', where 'val' is a valuation of variable 'var'
    :param epsilon: epsilon value for the automaton
    :param bloating: value for bloating invariants and guards
    :param hybrid_automaton: (optional) existing hybrid automaton for extension
    :return: hybrid automaton corresponding to the valuation
    """
    assert len(functions) > 0
    b_index = get_first_index_of_symbol(valuation=valuation, symbol='b')
    x_index = get_first_index_of_symbol(valuation=valuation[b_index:], symbol='x') + b_index

    for k, function in enumerate(functions):
        slopes_list, b_index = get_slopes_list(valuation=valuation, start_index=b_index, function_index=k+1)
        pwl_points_list, x_index = get_points_list(valuation=valuation, function=function, start_index=x_index,
                                                   function_index=k+1)
        hybrid_automaton_for_function = infer_hybrid_system_polyhedral_pwl(pwl_points_list=pwl_points_list,
                                                                           delta_ha=epsilon, delta_fh=bloating,
                                                                           pwl_slopes=slopes_list,
                                                                           only_consider_first_piece=False)
        if hybrid_automaton is None:
            hybrid_automaton = hybrid_automaton_for_function
        else:
            hybrid_automaton = merge(hybrid_automaton, hybrid_automaton_for_function)

    return hybrid_automaton
