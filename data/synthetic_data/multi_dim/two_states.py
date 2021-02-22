import pandas as pd

from data.synthetic_data.generator import construct_signal_from_run, sloped_line_df, straight_line_df
from data.synthetic_data.visualisation import plot_data, plot_multidim


@plot_data(plot_multidim)
def zig_zig_line_twod():

    sloped_lines_dict = {
        "a": sloped_line_df(1),
        "c": sloped_line_df(-1, start=1000)
    }

    run_list1 = ["a", "c", "a", "c", "a", "c"]
    run_list2 = ["c", "a", "c", "a", "c", "a"]

    dim1 = construct_signal_from_run(sloped_lines_dict, run_list1)
    dim2 = construct_signal_from_run(sloped_lines_dict, run_list2).rename(columns={"a": "b"})

    return pd.concat((dim1, dim2))


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")