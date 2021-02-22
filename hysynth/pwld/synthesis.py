from hysynth.utils.hybrid_system.library import get_delta_fh
from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwld import *
from hysynth.pwld.julia_bridge.library import load_julia_libraries


def ha_synthesis_from_pwld_functions(data, delta_ha, n_discrete_steps, refinement_distance, reachability_time_step,
                                     statistics=None, print_intermediate=None, log=False):
    """ Synthesize a hybrid automaton from piecewise-linear differential data

    Parameters
    ----------
    data : a list of triples (pwld, x0, epsilon) where
           - pwld is a piecewise-linear differential function given as another list of pairs (D, T) representing pieces
             with affine dynamics (AffDyn) D and time horizon T
           - x0 is the initial state
           - epsilon is the information of how close the piecewise-linear differential function

    delta_ha : the delta of the hybrid automaton
    """

    if not isinstance(data, list):
        raise TypeError("data must be a list of pairs!")

    if not isinstance(delta_ha, (int, float)):
        raise TypeError("delta_ha must be a numeric type!")

    # construct the initial_hybrid automaton from the first piecewise-linear differential function
    first_pwld_function, first_x0, first_epsilon = data[0]
    hybrid_automaton =\
        construct_automaton_from_pwld_function(pwld_sequence=first_pwld_function, delta_ha=delta_ha)

    return ha_adaptation_from_pwld_functions(data=data, hybrid_automaton=hybrid_automaton,
                                             n_discrete_steps=n_discrete_steps, refinement_distance=refinement_distance,
                                             reachability_time_step=reachability_time_step,
                                             print_intermediate=print_intermediate, statistics=statistics, log=log)


def ha_adaptation_from_pwld_functions(data, hybrid_automaton, n_discrete_steps, refinement_distance,
                                      reachability_time_step, statistics=None, print_intermediate=None, log=False):
    """ Adapt a hybrid automaton based on piecewise-linear differential data

    Parameters
    ----------
    data : a list of triples (pwld, x0, epsilon) where
           - pwld is a piecewise-linear differential function given as another list of pairs (D, T) representing pieces
             with affine dynamics (AffDyn) D and time horizon T
           - x0 is the initial state
           - epsilon is the information of how close the piecewise-linear differential function

    hybrid_automaton : the hybrid automaton being adapted
    """

    if not isinstance(data, list):
        raise TypeError("data must be a list of pairs!")

    if not isinstance(hybrid_automaton, HybridSystemPolyhedral):
        raise NotImplementedError("hybrid_automaton must be of type HybridSystemPolyhedral!")

    if print_intermediate is None:
        print_intermediate = []

    load_julia_libraries(log=log)

    delta_ha = hybrid_automaton.delta

    # iterate over the data
    data_index = 0
    for i, (pwld_function, x0, epsilon) in enumerate(data):
        if i in print_intermediate:
            print("---intermediate automaton after {:} iterations---{}".format(i, hybrid_automaton))
        data_index += 1
        delta_fh = get_delta_fh(delta_ha, epsilon)  # distance d(f, H)
        hybrid_automaton = adapt_automaton_to_pwld_function(pwld_function=pwld_function,
                                                            x0=x0,
                                                            hybrid_automaton=hybrid_automaton,
                                                            tube_radius=delta_fh,
                                                            data_index=data_index,
                                                            n_discrete_steps=n_discrete_steps,
                                                            refinement_distance=refinement_distance,
                                                            reachability_time_step=reachability_time_step,
                                                            statistics=statistics,
                                                            log=log)

        if log > 1:
            print("intermediate automaton: {}".format(hybrid_automaton))

    return hybrid_automaton
