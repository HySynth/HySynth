from data.synthetic_data.generator import construct_signal_from_run, sloped_line_df, straight_line_df
from data.synthetic_data.visualisation import plot_data, plot_1D


@plot_data(plot_1D)
def peaks():

    sloped_lines_dict = {
        "a": sloped_line_df(1),
        "b": sloped_line_df(-1, start=1000),
        "c": straight_line_df(0),
    }

    run_list = ["a", "b", "c", "a", "b", "c", "a", "b", "c", "a", "b", "c"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def valeys():

    sloped_lines_dict = {
        "a": sloped_line_df(1),
        "b": sloped_line_df(-1, start=1000),
        "c": straight_line_df(1000),
    }

    run_list = ["a", "c", "b", "a", "c", "b", "a", "c", "b", "a", "c", "b"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def valeys_shorter():

    sloped_lines_dict = {
        "a": sloped_line_df(1, num_points=50),
        "b": sloped_line_df(-1, start=50, num_points=50),
        "c": straight_line_df(50, num_points=50),
    }

    run_list = ["a", "c", "b", "a", "c"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")
