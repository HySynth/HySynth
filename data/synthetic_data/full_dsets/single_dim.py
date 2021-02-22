""" This module is a library of synthetic example datasets """


from data.synthetic_data.generator import construct_signal_from_run, sloped_line_df, straight_line_df
from data.synthetic_data.visualisation import plot_data, plot_1D


sloped_lines_dict = {
    "a": sloped_line_df(1, num_points=5),
    "b": sloped_line_df(-1, start=5, num_points=5),
    "c": straight_line_df(0, num_points=5),
    "d": straight_line_df(5, num_points=5)
}


@plot_data(plot_1D)
def peak():

    run_list = ["a", "b"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def valey():

    run_list = ["b", "a"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def ramp_on():

    run_list = ["b", "d"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def ramp_off():

    run_list = ["b", "c"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def rise():

    run_list = ["c", "a"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def drop():

    run_list = ["b", "d"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def wedge():

    run_list = ["a", "d", "b"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def chanel():

    run_list = ["b", "c", "a"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def peak_last():

    run_list = ["c", "a", "b"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def peak_first():

    run_list = ["a", "b", "c"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def zig_zag():

    run_list = ["a", "b", "a", "b"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def zig_zag_down():

    run_list = ["c", "a", "b", "a"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


@plot_data(plot_1D)
def zig_zag_up():

    run_list = ["a", "b", "a", "d"]

    return construct_signal_from_run(sloped_lines_dict, run_list)


def single_time_series_dataset_1():
    return [zig_zag()]


def single_time_series_dataset_2():
    return [peak_first()]


def single_time_series_dataset_3():
    return [wedge()]


def dataset_of_two_1():
    ts1 = zig_zag()
    ts2 = peak()

    return [ts1, ts2]


def dataset_of_three_same_1():
    ts1 = zig_zag()

    return [ts1, ts1, ts1]


def dataset_of_three_1():
    ts1 = zig_zag()
    ts2 = chanel()
    ts3 = valey()

    return [ts1, ts2, ts3]


def dataset_of_three_rev_1():
    ts1 = zig_zag()
    ts2 = chanel()
    ts3 = valey()

    return [ts3, ts2, ts1]

