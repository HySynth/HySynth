from pathlib import Path
import time

from hysynth.utils.hybrid_system import HybridSystemAffineDynamics, map_initial_condition
from hysynth.utils.dynamics import *
from hysynth.utils import Logger, Statistics, load_from_file, save_to_file
from hysynth.pwld import ha_adaptation_from_pwld_functions, ha_synthesis_from_pwld_functions,\
    simulate, plot_pwld_functions, time_series2pwld_function, plot_pwld_functions_and_time_series
from hysynth.pwld.julia_bridge.library import load_julia_libraries, reset_seed, set_flow, convert_pwld_julia2python,\
    convert_set_julia2python, Hyperrectangle_jl, HalfSpace_jl, HPolyhedron_jl, Interval_jl
from data.real_data.preprocess import data2array as load_time_series


def simulate_automaton(dataset, pwld_functions, hybrid_automaton, name, max_dwell_time, max_perturbation, n_simulations,
                       path_length, perturbation_ignored, time_step, i_delta_ha, min_dwell_time, log=False):
    xlim = max(ts[-1][0] for ts in dataset)
    initial_location = hybrid_automaton.locations[0]
    dim = len(dataset[0][0]) - 1
    if dim == 1:
        initial_points = [ts[0][1] for ts in dataset]
        lo = min(initial_points)
        hi = max(initial_points)
        if lo == hi:
            lo -= 1e-9
            hi += 1e-9
        initial_set = Interval_jl(lo, hi)
    else:
        initial_set = None
    if max_dwell_time is -1:
        max_dwell_time = []
        t_last = 0.0
        for dyn_t in pwld_functions[0][0]:
            duration = dyn_t[1] - t_last
            t_last = dyn_t[1]
            max_dwell_time.append(duration + 1e-2)
        path_length = min(path_length, len(max_dwell_time))
    if min_dwell_time is -1:
        min_dwell_time = []
        t_last = 0.0
        for dyn_t in pwld_functions[0][0]:
            duration = dyn_t[1] - t_last
            t_last = dyn_t[1]
            min_dwell_time.append(duration - 1e-2)
        path_length = min(path_length, len(min_dwell_time))

    initial_condition = {initial_location: initial_set}
    avoid_self_loops = True
    prefer_new_locations = True
    simulations_result = simulate(hybrid_automaton=hybrid_automaton, max_dwell_time=max_dwell_time,
                                  initial_condition=initial_condition, n_samples=n_simulations,
                                  max_perturbation=max_perturbation, path_length=path_length,
                                  perturbation_ignored=perturbation_ignored, time_step=time_step,
                                  min_dwell_time=min_dwell_time, avoid_self_loops=avoid_self_loops,
                                  prefer_new_locations=prefer_new_locations, log=log)
    file_names = ["{}_time_series_{:d}.pdf".format(name, i) for i in range(1, len(pwld_functions) + 1)]
    plot_pwld_functions_and_time_series(pwld_functions=pwld_functions, time_series=dataset, file_names=file_names,
                                        clean=False, xlim=xlim)
    plot_pwld_functions(simulations_result,
                        file_name="{}_{:d}_time_series_and_functions_combined.pdf".format(name, i_delta_ha),
                        color="g", xlim=xlim)
    plot_pwld_functions(pwld_functions[:n_simulations],
                        file_name="{}_{:d}_functions_original.pdf".format(name, i_delta_ha),
                        color="b", clean=False, xlim=xlim)
    plot_pwld_functions(simulations_result,
                        file_name="{}_{:d}_functions_combined.pdf".format(name, i_delta_ha), color="g", xlim=xlim)
    plot_pwld_functions(simulations_result,
                        file_name="{}_{:d}_functions_result.pdf".format(name, i_delta_ha), color="g", xlim=xlim)


def simulate_automata(hybrid_automaton_source, hybrid_automaton_synthesized, name, initial_condition, max_dwell_time,
                      max_perturbation, n_simulations, path_length, perturbation_ignored, pwld_functions, time_step,
                      min_dwell_time, i_delta_ha, phase_portrait=False, log=False):
    initial_condition_new = map_initial_condition(old_initial_condition=initial_condition,
                                                  old_automaton=hybrid_automaton_source,
                                                  new_automaton=hybrid_automaton_synthesized)

    avoid_self_loops = True
    prefer_new_locations = True
    simulations_result = simulate(hybrid_automaton=hybrid_automaton_synthesized,
                                  initial_condition=initial_condition_new, max_dwell_time=max_dwell_time,
                                  n_samples=n_simulations, max_perturbation=max_perturbation, path_length=path_length,
                                  perturbation_ignored=perturbation_ignored, time_step=time_step,
                                  min_dwell_time=min_dwell_time, avoid_self_loops=avoid_self_loops,
                                  prefer_new_locations=prefer_new_locations, log=log)
    plot_pwld_functions(pwld_functions[:n_simulations], phase_portrait=phase_portrait,
                        file_name="{}_{:d}_simulations_original.pdf".format(name, i_delta_ha), color="b", clean=False)
    plot_pwld_functions(simulations_result, phase_portrait=phase_portrait,
                        file_name="{}_{:d}_simulations_combined.pdf".format(name, i_delta_ha), color="g")
    plot_pwld_functions(simulations_result, phase_portrait=phase_portrait,
                        file_name="{}_{:d}_simulations_result.pdf".format(name, i_delta_ha), color="g")


def synthesize_automaton_from_pwld_functions(pwld_functions, load, name, delta_ha, statistics, n_discrete_steps,
                                             n_total, reachability_time_step, refinement_distance, i_delta_ha,
                                             n_intermediate, log):
    statistics.add(key="#pwld", value=len(pwld_functions))
    piece_lengths = [len(f[0]) for f in pwld_functions]
    statistics.add(key="avg pwld piece length", value=sum(piece_lengths)/len(piece_lengths))
    statistics.add(key="max pwld piece length", value=max(piece_lengths))
    statistics.add(key="min pwld piece length", value=min(piece_lengths))
    if load:
        file_name = "{}_{:d}_{:d}".format(name, i_delta_ha, n_total)
        hybrid_automaton_synthesized_2_py = HybridSystemAffineDynamics.load(filename=file_name)
    else:
        t0 = time.time()
        if n_intermediate > 0:
            hybrid_automaton_synthesized_1 = ha_synthesis_from_pwld_functions(
                data=pwld_functions[:n_intermediate], delta_ha=delta_ha, n_discrete_steps=n_discrete_steps,
                refinement_distance=refinement_distance, reachability_time_step=reachability_time_step,
                statistics=statistics, log=log)
            hybrid_automaton_synthesized_1_py = hybrid_automaton_synthesized_1.convert_automaton(
                convert_pwld_julia2python, convert_set_julia2python)
            hybrid_automaton_synthesized_1_py.save("{}_{:d}_{:d}".format(name, i_delta_ha, n_intermediate))
            print("Synthesized after {:d} steps:".format(n_intermediate), hybrid_automaton_synthesized_1)

            hybrid_automaton_synthesized_2 = ha_adaptation_from_pwld_functions(
                data=pwld_functions[n_intermediate:], hybrid_automaton=hybrid_automaton_synthesized_1,
                n_discrete_steps=n_discrete_steps, refinement_distance=refinement_distance,
                reachability_time_step=reachability_time_step, statistics=statistics, log=log)
            hybrid_automaton_synthesized_2_py = hybrid_automaton_synthesized_2.convert_automaton(
                convert_pwld_julia2python, convert_set_julia2python)
            hybrid_automaton_synthesized_2_py.save("{}_{:d}_{:d}".format(name, i_delta_ha, n_total))
        else:
            hybrid_automaton_synthesized_2 = ha_synthesis_from_pwld_functions(
                data=pwld_functions, delta_ha=delta_ha, n_discrete_steps=n_discrete_steps,
                refinement_distance=refinement_distance, reachability_time_step=reachability_time_step,
                statistics=statistics, log=log)
            hybrid_automaton_synthesized_2_py = hybrid_automaton_synthesized_2.convert_automaton(
                convert_pwld_julia2python, convert_set_julia2python)
            hybrid_automaton_synthesized_2_py.save("{}_{:d}_{:d}".format(name, i_delta_ha, n_total))
        print("Synthesized after {:d} steps:".format(n_total), hybrid_automaton_synthesized_2)
        statistics.add(key="synth time", value=time.time() - t0)
    statistics.add(key="synth #modes", value=len(hybrid_automaton_synthesized_2_py.locations))
    return hybrid_automaton_synthesized_2_py


def run_synthesis_from_simulations(seed, parameter_function, hybrid_automaton_function, name, statistics, load=False,
                                   phase_portrait=False, log=0):
    print("-------------\nRESULTS {} MODEL\n-------------".format(name))
    statistics.change_model(name)

    if seed is not None:
        reset_seed(seed)
    deltas_ha, initial_condition, max_dwell_time, max_perturbation, n_discrete_steps, n_intermediate, n_samples, \
        n_simulations, path_length, perturbation_ignored, reachability_time_step, refinement_distance, time_step,\
        min_dwell_time = parameter_function()
    pwld_functions = None
    n_total = -1

    for i_delta_ha, delta_ha in enumerate(deltas_ha):
        print("Consider delta = {:f}".format(delta_ha))
        statistics.change_delta(delta_ha)

        if seed is not None:
            reset_seed(seed)
        hybrid_automaton_source = hybrid_automaton_function(delta=delta_ha)
        if not load:
            hybrid_automaton_source_py = hybrid_automaton_source.convert_automaton(None, convert_set_julia2python)
            hybrid_automaton_source_py.save("{}_{:d}_original".format(name, i_delta_ha))
            if i_delta_ha == 0:
                print("Original:", hybrid_automaton_source)
        statistics.add_general(key="orig #modes", value=len(hybrid_automaton_source.locations))

        if i_delta_ha == 0:  # only simulate the first automaton (saves a lot of time)
            if seed is not None:
                reset_seed(seed)
            t0 = time.time()
            pwld_functions = simulate(hybrid_automaton=hybrid_automaton_source, initial_condition=initial_condition,
                                      max_dwell_time=max_dwell_time, n_samples=n_samples, max_perturbation=max_perturbation,
                                      path_length=path_length, perturbation_ignored=perturbation_ignored,
                                      time_step=time_step, log=log)
            statistics.add_general(key="sim time", value=time.time() - t0)
            n_total = len(pwld_functions)

        if seed is not None:
            reset_seed(seed)
        hybrid_automaton_synthesized_2_py = synthesize_automaton_from_pwld_functions(
            pwld_functions=pwld_functions, load=load, name=name, delta_ha=delta_ha, statistics=statistics,
            n_discrete_steps=n_discrete_steps, n_total=n_total, reachability_time_step=reachability_time_step,
            refinement_distance=refinement_distance, i_delta_ha=i_delta_ha, n_intermediate=n_intermediate, log=log)

        if seed is not None:
            reset_seed(seed)
        simulate_automata(hybrid_automaton_source=hybrid_automaton_source,
                          hybrid_automaton_synthesized=hybrid_automaton_synthesized_2_py,
                          initial_condition=initial_condition, max_dwell_time=max_dwell_time,
                          max_perturbation=max_perturbation, n_simulations=n_simulations, name=name,
                          path_length=path_length, perturbation_ignored=perturbation_ignored,
                          pwld_functions=pwld_functions, time_step=time_step, i_delta_ha=i_delta_ha,
                          phase_portrait=phase_portrait, min_dwell_time=min_dwell_time, log=log)

        n_nodes_list = statistics.get_delta_entry("list #tree nodes")
        statistics.add(key="total #nodes", value=sum(n_nodes_list))
        # n_nodes_max_list = statistics.get_delta_entry("list #tree nodes max")
        # statistics.add(key="total #nodes max", value=sum(n_nodes_max_list))


def run_synthesis_from_time_series(seed, parameter_function, dataset_function, name, statistics, load=False,
                                   save_pwld_functions=True, log=0):
    print("-------------\nRESULTS {} MODEL\n-------------".format(name))
    statistics.change_model(name)

    if seed is not None:
        reset_seed(seed)
    delta_ts, deltas_ha, n_discrete_steps, reachability_time_step, refinement_distance, max_dwell_time, n_intermediate,\
        n_simulations, path_length, time_step, min_dwell_time = parameter_function()
    max_perturbation = 0.0
    perturbation_ignored = 0

    if seed is not None:
        reset_seed(seed)
    dataset = dataset_function()
    n_total = len(dataset)

    file_name = "pwld_{}_{:d}_{:f}".format(name, n_total, delta_ts)
    if load:
        pwld_functions = load_from_file(file_name=file_name)
    else:
        if seed is not None:
            reset_seed(seed)
        t0 = time.time()
        pwld_functions = [time_series2pwld_function(ts, delta_ts, log=log) for ts in dataset]
        if save_pwld_functions:
            save_to_file(pwld_functions, file_name=file_name)
        statistics.add_general(key="ts2pwl time", value=time.time() - t0)

    for i_delta_ha, delta_ha in enumerate(deltas_ha):
        print("Consider delta = {:f}".format(delta_ha))
        statistics.change_delta(delta_ha)

        if seed is not None:
            reset_seed(seed)
        hybrid_automaton_synthesized_2_py = synthesize_automaton_from_pwld_functions(
            pwld_functions=pwld_functions, load=load, name=name, delta_ha=delta_ha, statistics=statistics,
            n_discrete_steps=n_discrete_steps, n_total=n_total, reachability_time_step=reachability_time_step,
            refinement_distance=refinement_distance, i_delta_ha=i_delta_ha, n_intermediate=n_intermediate, log=log)

        if seed is not None:
            reset_seed(seed)
        simulate_automaton(dataset=dataset, pwld_functions=pwld_functions,
                           hybrid_automaton=hybrid_automaton_synthesized_2_py, name=name, max_dwell_time=max_dwell_time,
                           max_perturbation=max_perturbation, n_simulations=n_simulations,  path_length=path_length,
                           perturbation_ignored=perturbation_ignored, time_step=time_step, i_delta_ha=i_delta_ha,
                           min_dwell_time=min_dwell_time, log=log)

        n_nodes_list = statistics.get_delta_entry("list #tree nodes")
        if n_nodes_list is not None:
            statistics.add(key="total #nodes", value=sum(n_nodes_list))
        # n_nodes_max_list = statistics.get_delta_entry("list #tree nodes max")
        # statistics.add(key="total #nodes max", value=sum(n_nodes_max_list))


def hybrid_automaton_heater(delta):
    ha = HybridSystemAffineDynamics(name="Heater", variable_names=["x"], delta=delta)

    a = 0.1

    ha.add_location("off")
    A = LinDyn([[-a]])
    set_flow(ha, "off", A)
    inv = Hyperrectangle_jl([20.0], [2.0])
    ha.set_invariant("off", inv)

    ha.add_location("on")
    A = AffDyn([[-a]], [30.0 * a])
    set_flow(ha, "on", A)
    ha.set_invariant("on", inv)

    ha.add_edge("off", "on")
    guard = Hyperrectangle_jl([18.5], [0.5])
    ha.set_guard(("off", "on"), guard)

    ha.add_edge("on", "off")
    guard = Hyperrectangle_jl([21.5], [0.5])
    ha.set_guard(("on", "off"), guard)

    return ha


def parameters_heater():
    deltas_ha = [0.1, 0.1, 0.07, 0.04, 0.01]

    n_samples = 100
    max_perturbation = 0.001
    path_length = 6
    max_dwell_time = 7.0
    min_dwell_time = None
    time_step = 0.05
    perturbation_ignored = 1
    initial_condition = None

    n_discrete_steps = 10
    refinement_distance = 1e-3
    reachability_time_step = 1e-3
    n_intermediate = 10

    n_simulations = 3

    return deltas_ha, initial_condition, max_dwell_time, max_perturbation, n_discrete_steps, n_intermediate, n_samples,\
        n_simulations, path_length, perturbation_ignored, reachability_time_step, refinement_distance, time_step,\
        min_dwell_time


def hybrid_automaton_gearbox(delta):
    # see "An Algorithmic Approach to Global Asymptotic Stability Verification of Hybrid Systems"
    # note: bug in paper: all omegas need to be swapped in the guards and also in the invariant of q1
    ha = HybridSystemAffineDynamics(name="Gearbox", variable_names=["v", "T_I"], delta=delta)

    M = 1500.0
    T = 40.0
    omega_l = 500.0
    omega_h = 230.0
    p1 = 50.0
    p2 = 32.0
    p3 = 20.0
    p4 = 14.0
    k1 = float(15/4)
    k2 = float(375/64)
    k3 = float(75/8)
    k4 = float(375/28)
    vd = 30.0

    a_v_leq = [1.0, 0.0]
    a_v_geq = [-1.0, 0.0]
    eps = 0.1  # bloating of hyperplanar guards to make simulation find them

    q1 = "q1"
    ha.add_location(q1)
    A1 = LinDyn([[-p1 * k1 / M, -p1 / M],
                 [k1 / T, 0.0]])
    set_flow(ha, q1, A1)
    inv = HalfSpace_jl(a_v_geq, -vd + 1/p1 * omega_l + eps)  # v >= vd - 1/p1 * omega_l  (bug!)
    ha.set_invariant(q1, inv)

    q2 = "q2"
    ha.add_location(q2)
    A2 = LinDyn([[-p2 * k2 / M, -p2 / M],
                 [k2 / T, 0.0]])
    set_flow(ha, q2, A2)
    inv = HPolyhedron_jl([HalfSpace_jl(a_v_geq, -vd + 1/p2 * omega_l + eps),  # v >= vd - 1/p2 * omega_l
                          HalfSpace_jl(a_v_leq, vd - 1/p2 * omega_h + eps)])  # v <= vd - 1/p2 * omega_h
    ha.set_invariant(q2, inv)

    q3 = "q3"
    ha.add_location(q3)
    A3 = LinDyn([[-p3 * k3 / M, -p3 / M],
                 [k3 / T, 0.0]])
    set_flow(ha, q3, A3)
    inv = HPolyhedron_jl([HalfSpace_jl(a_v_geq, -vd + 1/p3 * omega_l + eps),  # v >= vd - 1/p3 * omega_l
                          HalfSpace_jl(a_v_leq, vd - 1/p3 * omega_h + eps)])  # v <= vd - 1/p3 * omega_h
    ha.set_invariant(q3, inv)

    q4 = "q4"
    ha.add_location(q4)
    A4 = LinDyn([[-p4 * k4 / M, -p4 / M],
                 [k4 / T, 0.0]])
    set_flow(ha, q4, A4)
    inv = HalfSpace_jl(a_v_leq, vd - 1/p4 * omega_h + eps)  # v <= vd - 1/p4 * omega_l
    ha.set_invariant(q4, inv)

    ha.add_edge(q1, q2)
    b = vd - 1/p1 * omega_l  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p1 * omega_l
    ha.set_guard((q1, q2), guard)

    ha.add_edge(q2, q1)
    b = vd - 1/p2 * omega_h  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p2 * omega_h
    ha.set_guard((q2, q1), guard)

    ha.add_edge(q2, q3)
    b = vd - 1/p2 * omega_l  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p2 * omega_l
    ha.set_guard((q2, q3), guard)

    ha.add_edge(q3, q2)
    b = vd - 1/p3 * omega_h  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p3 * omega_h
    ha.set_guard((q3, q2), guard)

    ha.add_edge(q3, q4)
    b = vd - 1/p3 * omega_l  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p3 * omega_l
    ha.set_guard((q3, q4), guard)

    ha.add_edge(q4, q3)
    b = vd - 1/p4 * omega_h  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p4 * omega_h
    ha.set_guard((q4, q3), guard)

    return ha


def parameters_gearbox():
    deltas_ha = [0.1, 0.1, 0.07, 0.04, 0.01]

    n_samples = 10
    max_perturbation = 0.0001
    path_length = 4
    max_dwell_time = 40.0
    min_dwell_time = None
    time_step = 0.02
    perturbation_ignored = 1
    initial_condition = {"q1": Hyperrectangle_jl([27.0, 0.0], [1.0, 1e-9]),
                        # "q4": Hyperrectangle_jl([-3.0, 0.0], [2.0, 1e-9])
                        }

    n_discrete_steps = 10
    refinement_distance = 1e-3
    reachability_time_step = 1e-3
    n_intermediate = 0

    n_simulations = 3

    return deltas_ha, initial_condition, max_dwell_time, max_perturbation, n_discrete_steps, n_intermediate, n_samples,\
        n_simulations, path_length, perturbation_ignored, reachability_time_step, refinement_distance, time_step,\
        min_dwell_time


def time_series_ecg():
    path = Path(__file__).parent.parent / "data" / "real_data" / "datasets" / "ekg_data"
    filename1 = path / "ekg_1.csv"
    filename2 = path / "ekg_2.csv"
    filename3 = path / "ekg_3.csv"
    f1 = load_time_series(filename1, 2)
    f2 = load_time_series(filename2, 2)
    f3 = load_time_series(filename3, 2)
    dataset = [f1, f2, f3]
    return dataset


def time_series_ecg2():
    f1, f2, f3 = time_series_ecg()
    dataset = [f1, f3, f2]
    return dataset


def time_series_ecg3():
    f1, f2, f3 = time_series_ecg()
    dataset = [f2, f1, f3]
    return dataset


def time_series_ecg4():
    f1, f2, f3 = time_series_ecg()
    dataset = [f2, f3, f1]
    return dataset


def time_series_ecg5():
    f1, f2, f3 = time_series_ecg()
    dataset = [f3, f1, f2]
    return dataset


def time_series_ecg6():
    f1, f2, f3 = time_series_ecg()
    dataset = [f3, f2, f1]
    return dataset


def get_time_series_ecg_function(i):
    if i == 1:
        return time_series_ecg
    elif i == 2:
        return time_series_ecg2
    elif i == 3:
        return time_series_ecg3
    elif i == 4:
        return time_series_ecg4
    elif i == 5:
        return time_series_ecg5
    elif i == 6:
        return time_series_ecg6
    raise(ValueError("no function available for i = {}".format(i)))


def parameters_ecg(delta_ts):
    deltas_ha = [0.1]
    n_discrete_steps = 10
    reachability_time_step = 1e-3
    refinement_distance = 0.001
    n_intermediate = 1
    # use different simulation settings
    if delta_ts == 0.02:
        max_dwell_time = [3.7, 0.5, 0.6, 0.2, 0.1, 0.2, 2.0, 1.5, 2.0]
        min_dwell_time = [3.5, 0.4, 0.5, 0.1, 0.0, 0.1, 1.9, 1.4, 1.9]
        path_length = 8
    elif delta_ts == 0.05:
        max_dwell_time = [4.6, 0.3, 0.4, 1.4, 1.7, 3.0]
        min_dwell_time = [4.3, 0.1, 0.2, 1.1, 1.6, 2.0]
        path_length = 6
    else:
        raise(ValueError("undefined parameters for delta = ", delta_ts))
    n_simulations = 3
    time_step = 0.01
    return delta_ts, deltas_ha, n_discrete_steps, reachability_time_step, refinement_distance, max_dwell_time,\
        n_intermediate, n_simulations, path_length, time_step, min_dwell_time


def parameters_ecg_02():
    return parameters_ecg(0.02)


def parameters_ecg_05():
    return parameters_ecg(0.05)


# heater benchmark
def run_heater(load=False, log=0):
    logger = Logger.start("log_experiment_heater.txt")
    load_julia_libraries(log=True)
    seed = 1234

    statistics = Statistics()
    run_synthesis_from_simulations(seed=seed, parameter_function=parameters_heater,
                                   hybrid_automaton_function=hybrid_automaton_heater, name="heater",
                                   statistics=statistics, load=load, log=log)
    print(statistics)
    logger.stop()


# gearbox benchmark
def run_gearbox(load=False, log=0):
    logger = Logger.start("log_experiment_gearbox.txt")
    load_julia_libraries(log=True)
    seed = 1234

    statistics = Statistics()
    run_synthesis_from_simulations(seed=seed, parameter_function=parameters_gearbox,
                                   hybrid_automaton_function=hybrid_automaton_gearbox, name="gearbox",
                                   statistics=statistics, load=load, phase_portrait=True, log=log)
    print(statistics)
    logger.stop()


# ECG benchmark
def run_ecg(load=False, log=0):
    logger = Logger.start("log_experiment_ecg.txt")
    load_julia_libraries(log=True)
    seed = 1234

    for i in [1]:
        save_pwld_functions = i == 1
        # delta = 0.02 and delta = 0.05
        for parameter_function in [parameters_ecg_02, parameters_ecg_05]:
            statistics = Statistics()
            run_synthesis_from_time_series(seed=seed, parameter_function=parameter_function,
                                           dataset_function=get_time_series_ecg_function(i),     name="ecg_order{:d}".format(i),
                                           statistics=statistics, load=load, save_pwld_functions=save_pwld_functions, log=log)
            print(statistics)
    logger.stop()


def run_all():
    load_julia_libraries(log=True)
    load = False
    log = 0
    run_heater(load=load, log=log)
    run_gearbox(load=load, log=log)
    run_ecg(load=load, log=log)


if __name__ == "__main__":
    run_all()
