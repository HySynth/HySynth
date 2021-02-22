# to run this, add code from experiments_HSCC2021.py

def time_series_pulse():
    path = Path(__file__).parent.parent / "data" / "real_data" / "datasets" / "basic_data"
    filename1 = path / "pulse1-1.csv"
    filename2 = path / "pulse1-2.csv"
    filename3 = path / "pulse1-3.csv"
    f1 = load_time_series(filename1, 1)
    f2 = load_time_series(filename2, 1)
    f3 = load_time_series(filename3, 1)
    dataset = [f1, f2, f3]
    return dataset


def parameters_pulse():
    delta_ts = 0.02
    deltas_ha = [0.1]
    n_discrete_steps = 10
    reachability_time_step = 1e-3
    refinement_distance = 0.001
    n_intermediate = 1
    max_dwell_time = 4.0
    min_dwell_time = None
    n_simulations = 3
    path_length = 6
    time_step = 0.01
    return delta_ts, deltas_ha, n_discrete_steps, reachability_time_step, refinement_distance, max_dwell_time,\
        n_intermediate, n_simulations, path_length, time_step, min_dwell_time
