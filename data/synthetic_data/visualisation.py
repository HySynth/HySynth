""" This module contains the main functions for visualising synthetic data """
import functools
import numpy as np
import matplotlib.pyplot as plt


def plot_data(plotting_function, *plotargs, **plotkwargs):
    """ This function is a decorator generator function

    The output of this function is a function based on the arguments provided
    The outputting function actually wraps, the function that was decorated in order to:
     plot the data generated for easy visualisation

    """

    # wrap the decorator, to be able to pass, plotting functions
    def _plot(func):

        # wrap the original function
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):

            # check if plot was invoked
            if kwargs.get("plot", None):

                # remove the plot argument from kwargs, since its not used in the wrapped function
                del kwargs["plot"]

                # run the function that generates the data and pass any remaining arguments to it
                returned_data = func(*args, **kwargs)

                # check if there was a plot_name specified
                if plotkwargs.get("plot_name", None):
                    plot_name = plotkwargs["plot_name"]
                else:
                    plot_name = func.__name__

                # now plot the gotten data, and pass any arguments originally defined for plotting
                plotting_function(returned_data, plot_name, *plotargs, **plotkwargs)

                # now return the data once the plotting is closed
                return returned_data

            # if not just return the data
            else:
                return func(*args, **kwargs)

        # unroll
        return _wrapper
    return _plot


def plot_1D(timeseries_df, name):
    """ This is the function that corresponds to plotting 1D data """

    # create figure
    fig = plt.figure(figsize=(10, 6))

    # give it a name
    fig.suptitle(name, fontsize="20")

    plt.plot(timeseries_df.values)
    plt.show()


def plot_multidim(timeseries_df, name):
    """ This function corresponds to plotting multidimensional data """
    # create figure
    fig = plt.figure(figsize=(10, 6))

    # give it a name
    fig.suptitle(name, fontsize="20")

    # figure out the needed grid
    num_vals, num_dim = timeseries_df.shape
    grid_size = num_dim, 1

    x_coords = np.arange(0, num_vals)

    # plot individual dimensions
    for dim_n, dim_name in enumerate(timeseries_df.columns):
        current_ax = plt.subplot2grid(grid_size, (dim_n, 0))
        current_ax.plot(x_coords, dim_name, data=timeseries_df)
        current_ax.set_title(f"Signal of {dim_name}", fontsize="16")
        current_ax.set_xlabel("time", fontsize="14")
        current_ax.set_ylabel(dim_name, fontsize="14")

    plt.subplots_adjust(hspace=1.2, top=0.8)

    plt.show()


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")
