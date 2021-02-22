import networkx as nx

from data.synthetic_data.generator import sloped_line_df, construct_signal_from_run

from hysynth.pwl.hakimi_pwl import make_pwl_graph
from hysynth.pwl.initial_inference import infer_hybrid_system_polyhedral_pwl
from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


def test_initial_hs_with_example_ts_1():
    sloped_lines_dict = {
        "↗start": sloped_line_df(1, num_points=2),
        "↗": sloped_line_df(1, start=1, num_points=5),
        "↘": sloped_line_df(-1, start=5, num_points=5),
    }
    run_list = ["↗start", "↗", "↘", "↗"]
    data = construct_signal_from_run(sloped_lines_dict, run_list)

    # first transform the data into a tuple (x, y) list
    polyline_from_data = [(x, y) for x, y in enumerate(data[get_var(1)].values.tolist())]

    # run the make graph algo, epsilon is the hakimi setting (since we have no noise we can put it low
    pwl_graph = make_pwl_graph(polyline_from_data, epsilon=0.5)

    pwl_paths = nx.all_shortest_paths(pwl_graph, polyline_from_data[0], polyline_from_data[-1])

    # this avoids generating all paths, since we take just the first one (saves memory and time)
    hakimi_path = pwl_paths.__next__()

    ha = infer_hybrid_system_polyhedral_pwl(hakimi_path, delta_ha=1.0, delta_fh=0.5)
