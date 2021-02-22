# standard library
import math

# external packages
import pandas as pd
import networkx as nx

# internal packages
from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwl.hakimi_pwl.hakimi_algorithm import create_approximation_graph
from hysynth.pwl.initial_inference import infer_hybrid_system_polyhedral_pwl
from hysynth.pwl.membership import membership_info
from hysynth.pwl.adaptation import adapt_ha, relax_ha
from hysynth.pwl.library import check_clustering_bandwidth, tube
from hysynth.utils.hybrid_system.library import construct_variable_name, get_delta_fh

# define some global constants
EPSILON_DELTA_RATIO = 2.


def ha_synthesis_from_data_pwl(timeseries_data, delta_ha, pwl_epsilon=None, clustering_bandwidth=None,
                               allow_zero_delta=False):
    """ This function synthesises a hybrid automaton model from time-series data

    Parameters
    ----------
    timeseries_data : the full timeseries dataset

    delta_ha : the delta of the hybrid automaton

    pwl_epsilon : epsilon used for piecewise linear construction
                    if it is None, it defaults to the EPSILON_DELTA_RATIO

    clustering_bandwidth : the bandwidth used for the clustering procedure,
                            if False it disables clustering

    allow_zero_delta : option to allow a delta that is close to zero
    """

    if not (isinstance(timeseries_data, list) or isinstance(timeseries_data, pd.DataFrame)):
        raise TypeError("The argument timeseries_data must be a list or a Pandas DataFrame")

    if not isinstance(delta_ha, (int, float)):
        raise TypeError("delta_ha must be a numeric type!")

    if pwl_epsilon is None:
        pwl_epsilon = delta_ha / EPSILON_DELTA_RATIO

    elif not isinstance(pwl_epsilon, (int, float)):
        raise TypeError("pwl_epsilon must be a numeric type!")

    if clustering_bandwidth is None:
        clustering_bandwidth = delta_ha
    check_clustering_bandwidth(clustering_bandwidth)

    # get the piecewise linear approximation for the first time-series
    if isinstance(timeseries_data, list):
        first_pwl = get_pwl(time_series=timeseries_data[0],
                            pwl_epsilon=pwl_epsilon)

    elif isinstance(timeseries_data, pd.DataFrame):
        first_pwl = get_pwl(time_series=next(_data_iterator(timeseries_data))[1],  #
                            pwl_epsilon=pwl_epsilon)

    else:
        raise NotImplementedError("Unsupported data type!")

    # distance d(f, H), distance between the PWL function and hybrid automaton executions
    delta_fh = get_delta_fh(delta_ha, pwl_epsilon, allow_zero_delta=allow_zero_delta)

    # construct the initial_hybrid_automaton
    hybrid_automaton = infer_hybrid_system_polyhedral_pwl(pwl_points_list=first_pwl,
                                                          delta_ha=delta_ha,
                                                          delta_fh=delta_fh,
                                                          epsilon_meanshift=clustering_bandwidth)

    return ha_adaptation_from_data_pwl(data=timeseries_data,
                                       hybrid_automaton=hybrid_automaton,
                                       pwl_epsilon=pwl_epsilon,
                                       allow_zero_delta=allow_zero_delta)


def ha_adaptation_from_data_pwl(data, hybrid_automaton, pwl_epsilon=None, allow_zero_delta=False,
                                data_is_pwl_functions=False):
    """ This function adapts a given hybrid automaton based on the provided time-series data

    Parameters
    ----------
    data : The time-series data or PWL functions on which the adaptation will run

    hybrid_automaton : The hybrid automaton being adapted (must be hybrid automaton class)

    pwl_epsilon : The epsilon used for PWL construction

    allow_zero_delta : option to allow a delta that is close to zero

    data_is_pwl_functions : if True, we interpret the data as PWL functions; if False, we interpret
                            the data as time series

    """

    if not isinstance(hybrid_automaton, HybridSystemPolyhedral):
        raise NotImplementedError("The given hybrid_automaton must be a HybridSystemPolyhedral class")

    # extract delta from Hybrid automaton
    delta_ha = hybrid_automaton.delta

    if pwl_epsilon is None:
        pwl_epsilon = delta_ha / EPSILON_DELTA_RATIO

    elif not isinstance(pwl_epsilon, (int, float)):
        raise TypeError("pwl_epsilon must be a numeric type!")

    # distance d(f, H), distance between the PWL function and hybrid automaton executions
    delta_fh = get_delta_fh(delta_ha, pwl_epsilon, allow_zero_delta=allow_zero_delta)

    if not (isinstance(data, list) or isinstance(data, pd.DataFrame)):
        raise TypeError("data must be a list or a Pandas DataFrame")

    # iterate over the time-series
    for ts_index, current_data in _data_iterator(data):

        # construct pwls using the computed epsilon
        if data_is_pwl_functions:
            current_pwl_f = current_data
        else:
            current_pwl_f = get_pwl(time_series=current_data, pwl_epsilon=pwl_epsilon)
        ftube = tube(current_pwl_f, delta_fh)

        # compute the membership
        membership_passed, mem_info = membership_info(pwl_path=current_pwl_f,
                                                      hybrid_automaton=hybrid_automaton,
                                                      ftube=ftube)

        # check if membership is ok
        if membership_passed is False:

            # try to relax_ha the constraints, if success return a new HA, otherwise None
            relaxation_result = relax_ha(pwl_f=current_pwl_f,
                                         hybrid_automaton=hybrid_automaton,
                                         ftube=ftube)

            if relaxation_result is None:

                # adapt hybrid automaton
                hybrid_automaton = adapt_ha(current_pwl_f=current_pwl_f,
                                            hybrid_automaton=hybrid_automaton,
                                            data_index=ts_index,
                                            mem_info=mem_info,
                                            ftube=ftube)

            else:
                hybrid_automaton = relaxation_result

    return hybrid_automaton


def _data_iterator(time_series_data):
    if isinstance(time_series_data, list):

        return enumerate(time_series_data)

    elif isinstance(time_series_data, pd.DataFrame):

        def gen_iter():
            for index, series in time_series_data.iterrows():
                yield index, pd.DataFrame({construct_variable_name(1): series}).dropna()  # Very important to drop NaN

        return gen_iter()

    else:
        raise NotImplementedError("This is an unsupported data type!")


def get_pwl(time_series, pwl_epsilon):
    """ This is a wrapper function for getting a bounded piecewise linear approximation of the data """

    if not isinstance(pwl_epsilon, (int, float)):
        raise TypeError("pwl_epsilon must be a numeric type!")

    if not (isinstance(time_series, pd.DataFrame) or isinstance(time_series, list)):
        raise TypeError("The argument time_series must be a Pandas Dataframe, or a list!")

    if isinstance(time_series, pd.DataFrame):
        # just how hakimis algorithm wants the data
        polyline_from_data = list(zip(time_series.index.tolist(),
                                      time_series[construct_variable_name(1)].values.tolist()))

    else:
        polyline_from_data = time_series

    if math.isclose(pwl_epsilon, 0.0):

        return polyline_from_data

    else:

        approx_grap = create_approximation_graph(timeseries=polyline_from_data, epsilon=pwl_epsilon)

        shortest_path_gen =\
            nx.all_shortest_paths(approx_grap, tuple(polyline_from_data[0]), tuple(polyline_from_data[-1]))

        # this avoids generating all paths, since we take just the first one (saves memory and time)
        return next(shortest_path_gen)
