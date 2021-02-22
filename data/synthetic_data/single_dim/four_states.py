from data.synthetic_data.generator import construct_signal_from_run, sloped_line_df, straight_line_df
from data.synthetic_data.visualisation import plot_data, plot_1D


@plot_data(plot_1D)
def zigzagbox():

    sloped_lines_dict = {
        "a": sloped_line_df(1),
        "c": sloped_line_df(-1, start=1000),
        "g": straight_line_df(1000),
        "h": straight_line_df(0)
    }

    run_list = ["a", "g", "c", "h", "a", "g", "c", "h", "a", "g", "c", "h", "a", "g", "c", "h"]
    return construct_signal_from_run(sloped_lines_dict, run_list)

if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")