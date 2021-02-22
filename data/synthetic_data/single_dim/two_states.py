""" This module contains a library of functions that generate data with two different states """

import numpy as np

from data.synthetic_data.generator import construct_signal_from_run, sloped_line_df, straight_line_df
from data.synthetic_data.visualisation import plot_data, plot_1D


@plot_data(plot_1D)
def zig_zag_line():

    sloped_lines_dict = {
        "a": sloped_line_df(1),
        "c": sloped_line_df(-1, start=1000),
    }

    run_list = ["a", "c", "a", "c", "a", "c"]
    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def zig_zag_line_variable():

    sloped_lines_dict = {
        "a1": sloped_line_df(1),
        "a2": sloped_line_df(0.99),
        "a3": sloped_line_df(1.01),
        "a4": sloped_line_df(1.02),
        "b1": sloped_line_df(-1.015, start=1000),
        "b2": sloped_line_df(-0.99, start=1000),
        "b3": sloped_line_df(-0.98, start=1000),
        "b4": sloped_line_df(-0.975, start=1000),
    }

    run_list = ["a1", "b2", "a2", "b4", "a3", "b2", "a1", "b1", "a4", "b1", "a4", "b3", "a2", "b4"]
    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def zig_zag_line_more_variable():

    sloped_lines_dict = {
        "a1": sloped_line_df(1),
        "a2": sloped_line_df(0.8),
        "a3": sloped_line_df(1.1),
        "a4": sloped_line_df(1.15),
        "b1": sloped_line_df(-1.15, start=1000),
        "b2": sloped_line_df(-0.90, start=1000),
        "b3": sloped_line_df(-0.85, start=1000),
        "b4": sloped_line_df(-0.8, start=1000),
    }

    run_list = ["a1", "b2", "a2", "b4", "a3", "b2", "a1", "b1", "a4", "b1", "a4", "b3", "a2", "b4"]
    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def zig_zag_line_variable_noise():
    sloped_lines_dict = {
        "a1": sloped_line_df(1),
        "a2": sloped_line_df(0.99),
        "a3": sloped_line_df(1.01),
        "a4": sloped_line_df(1.02),
        "b1": sloped_line_df(-1.015, start=1000),
        "b2": sloped_line_df(-0.99, start=1000),
        "b3": sloped_line_df(-0.98, start=1000),
        "b4": sloped_line_df(-0.975, start=1000),
    }

    run_list = ["a1", "b2", "a2", "b4", "a3", "b2", "a1", "b1", "a4", "b1", "a4", "b3", "a2", "b4"]

    data = construct_signal_from_run(sloped_lines_dict, run_list)

    noise_term = np.random.normal(1, 5, data.shape[0])

    data = data.assign(a=lambda x: x.a + noise_term)

    return data


@plot_data(plot_1D)
def boxes():

    sloped_lines_dict = {
        "g": straight_line_df(1000),
        "h": straight_line_df(0),
    }

    run_list = ["g", "h", "g", "h", "g", "h", "g", "h"]
    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def boxes_variable():

    sloped_lines_dict = {
        "g1": straight_line_df(1000.1),
        "g2": straight_line_df(1000.2),
        "g3": straight_line_df(1000),
        "g4": straight_line_df(999.7),
        "h1": straight_line_df(0.1),
        "h2": straight_line_df(-0.1),
        "h3": straight_line_df(0),
        "h4": straight_line_df(0.2),
    }

    run_list = ["g2", "h1", "g4", "h3", "g3", "h1", "g3", "h2", "g1", "h4", "g2", "h1", "g4", "h2", "g1", "h1"]
    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def boxes_variable_noise():

    sloped_lines_dict = {
        "g1": straight_line_df(1000.1),
        "g2": straight_line_df(1000.2),
        "g3": straight_line_df(1000),
        "g4": straight_line_df(999.7),
        "h1": straight_line_df(0.1),
        "h2": straight_line_df(-0.1),
        "h3": straight_line_df(0),
        "h4": straight_line_df(0.2),
    }

    run_list = ["g2", "h1", "g4", "h3", "g3", "h1", "g3", "h2", "g1", "h4", "g2", "h1", "g4", "h2", "g1", "h1"]

    data = construct_signal_from_run(sloped_lines_dict, run_list)

    noise_term = np.random.normal(1, 5, data.shape[0])

    data = data.assign(a=lambda x: x.a + noise_term)

    return data


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")
