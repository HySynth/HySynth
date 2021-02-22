from data.synthetic_data.generator import sloped_line_df, straight_line_df
from data.synthetic_data.visualisation import plot_data, plot_1D


@plot_data(plot_1D)
def single_sloped_line1():
    return sloped_line_df(1)


@plot_data(plot_1D)
def single_sloped_line2():
    return sloped_line_df(2)


@plot_data(plot_1D)
def single_sloped_line05():
    return sloped_line_df(0.5)


@plot_data(plot_1D)
def single_sloped_line_min1():
    return sloped_line_df(-1, start=1000)


@plot_data(plot_1D)
def single_sloped_line_min2():
    return sloped_line_df(-2, start=2000)


@plot_data(plot_1D)
def single_sloped_line_min05():
    return sloped_line_df(-0.5, start=500)


@plot_data(plot_1D)
def single_sloped_line_min1_s0():
    return sloped_line_df(-1)


@plot_data(plot_1D)
def single_straight_line_5():
    return straight_line_df(5)


@plot_data(plot_1D)
def single_straight_line_min5():
    return straight_line_df(-5)


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")
