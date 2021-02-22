import random
import numpy as np

from hysynth.pwl.initial_inference import infer_hybrid_system_polyhedral_pwl as first_run
from hysynth.pwl.hysynth_pwl import ha_adaptation_from_data_pwl as further_runs
from hysynth.pwl.simulation.simulation_core import generate_pwl_from_ha as simulate, DEFAULT_TIME


def ha_synthesis_from_automaton(ha, delta_ha, iterations, pwl_epsilon=None, clustering_bandwith=0.5, seed=None,
                                max_jumps=5, time_bound=DEFAULT_TIME):
    """
    create a hybrid automaton using the synthesis algorithm by sampling simulations from a given automaton

    :param ha: hybrid automaton
    :param delta_ha: delta for the synthesis algorithm
    :param iterations: number of iterations of the synthesis loop
    :param pwl_epsilon: epsilon for the synthesis algorithm
    :param clustering_bandwith: clustering bandwidth the synthesis algorithm
    :return: a new hybrid automaton
    """
    if not (seed is None):
        random.seed(1234)
        np.random.seed(1234)

    num_jumps = random.randint(0, max_jumps)
    single_data = simulate(num_jumps, ha)
    ha_new = first_run(pwl_points_list=single_data,
                       delta_diff=delta_ha,
                       epsilon_meanshift=clustering_bandwith)

    dataset = list()

    for i in range(2, iterations + 1):
        num_jumps = random.randint(0, max_jumps)
        single_data = simulate(num_jumps, ha)
        dataset.append(single_data)

    ha_new = further_runs(data=dataset, hybrid_automaton=ha_new, pwl_epsilon=pwl_epsilon)

    return ha_new

