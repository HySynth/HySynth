""" This module is the main data generation module

It containts all the primitives for generating the data that can
later on be used to construct more complex synthetic data structures

"""

import numpy as np
import pandas as pd

from hysynth.utils.hybrid_system.library import construct_variable_name as get_var


def sloped_line_df(line_slope, start=0, num_points=1000):
    """ This function generates a sloped line

    The number of points is important because it corresponds to how long the
    duration of the line will be as well as the last value it hits


    """
    x_coords = np.arange(start=0, stop=num_points)
    y_coords = line_slope * x_coords + start
    return pd.DataFrame({get_var(1): y_coords})


def straight_line_df(line_val, num_points=1000):
    """ This function generates a straight line by just repeating a given value """
    return pd.DataFrame({get_var(1): np.repeat(line_val, repeats=num_points)})


def construct_signal_from_run(components_dict, run_list):
    """ This function is used to construct a signal run from two components
        a component dict, which maps a synth data primitive to a string
        a run list which is a list of strings, representing the desired sequence of components
    """
    return pd.concat(map(lambda seg: components_dict[seg], run_list))


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")

