from hysynth.pwld import sample_trajectory_pwld, ha_synthesis_from_pwld_functions
from hysynth.pwld.julia_bridge.library import trajectory2pwld_function


def simulate(hybrid_automaton, initial_condition, max_dwell_time, max_perturbation, n_samples, path_length,
             perturbation_ignored, time_step, min_dwell_time=None, avoid_self_loops=False, prefer_new_locations=False,
             log=False):
    pwld_functions = []
    if log:
        print("starting simulations with max. perturbation {} (but not for the first {:d} cases)".format(
            max_perturbation, perturbation_ignored))
    for i in range(n_samples):
        if i < perturbation_ignored:
            new_max_perturbation = 0.0
        else:
            new_max_perturbation = max_perturbation
        trajectory = sample_trajectory_pwld(hybrid_automaton=hybrid_automaton, path_length=path_length,
                                            max_dwell_time=max_dwell_time, time_step=time_step,
                                            initial_condition=initial_condition, max_perturbation=new_max_perturbation,
                                            min_dwell_time=min_dwell_time, avoid_self_loops=avoid_self_loops,
                                            prefer_new_locations=prefer_new_locations, log=log)
        pwld_function = trajectory2pwld_function(trajectory=trajectory, hybrid_automaton=hybrid_automaton)
        if log:
            print(trajectory)
        pwld_functions.append(pwld_function)
    return pwld_functions


def imitate_hybrid_automaton_pwld(hybrid_automaton, delta_ha, n_samples, path_length, max_dwell_time, time_step,
                                  n_discrete_steps, refinement_distance, reachability_time_step, max_perturbation,
                                  print_intermediate=None, perturbation_ignored=0, initial_condition=None, log=False):
    pwld_functions = simulate(hybrid_automaton, initial_condition, max_dwell_time, max_perturbation, n_samples,
                              path_length, perturbation_ignored, time_step, log=log)

    if log:
        print("finished sampling {:d} trajectories; starting synthesis".format(len(pwld_functions)))
    new_automaton = ha_synthesis_from_pwld_functions(data=pwld_functions, delta_ha=delta_ha,
                                                     n_discrete_steps=n_discrete_steps,
                                                     refinement_distance=refinement_distance,
                                                     reachability_time_step=reachability_time_step,
                                                     print_intermediate=print_intermediate, log=log)
    return new_automaton
