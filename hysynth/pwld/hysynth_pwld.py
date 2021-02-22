from hysynth.pwld import ha_synthesis_from_pwld_functions as synthesis


def ha_synthesis_from_pwld_functions(data, delta_ha, n_discrete_steps, refinement_distance, reachability_time_step,
                                     print_intermediate=None, log=False):
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
    return synthesis(data, delta_ha, n_discrete_steps, refinement_distance, reachability_time_step,
                     print_intermediate=print_intermediate, log=log)
