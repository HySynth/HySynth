import random
import numpy as np
import pandas as pd
import json

from scipy.interpolate import interp1d

from .simulation_core import generate_pwl_from_ha, generate_pwl_from_ha_with_time_horizon


def generate_pwl_dataset(hybrid_automaton, n_iterations, max_jumps=None, seed=True, time_bound=None, longest_first=True,
                         starting_positions=False, time_horizon=None, long_paths=True):

    if seed is True:
        random.seed(1234)
        np.random.seed(1234)
    elif seed is not False:
        random.seed(seed)
        np.random.seed(seed)

    dataset = list()

    for _ in range(n_iterations):
        if not long_paths:
            # allow shorter paths
            max_jumps = random.randint(0, max_jumps)

        if time_bound is None and time_horizon is None:
            current_simulation_ts = generate_pwl_from_ha(number_of_transitions=max_jumps,
                                                         hybrid_automaton=hybrid_automaton,
                                                         starting_positions=starting_positions)
        elif time_bound is not None and time_horizon is None:
            current_simulation_ts = generate_pwl_from_ha(number_of_transitions=max_jumps,
                                                         hybrid_automaton=hybrid_automaton,
                                                         time_bound=time_bound,
                                                         starting_positions=starting_positions)

        elif time_bound is None and time_horizon is not None:
            current_simulation_ts = generate_pwl_from_ha_with_time_horizon(hybrid_automaton=hybrid_automaton,
                                                                           starting_positions=starting_positions,
                                                                           time_horizon=time_horizon)

        elif time_bound is not None and time_horizon is not None:
            current_simulation_ts = generate_pwl_from_ha_with_time_horizon(hybrid_automaton=hybrid_automaton,
                                                                           starting_positions=starting_positions,
                                                                           time_horizon=time_horizon,
                                                                           time_bound=time_bound)

        else:
            raise RuntimeError("This can never happen!")

        dataset.append(current_simulation_ts)

    if longest_first:
        longest_index, simulation = max([(i, sim) for i, sim in enumerate(dataset)], key=lambda x: len(x[1]))

        del dataset[longest_index]

        dataset = [simulation] + dataset

    return dataset


def generate_timeseries_dataset(pwl_dataset, sampling_frequency):
    """  """

    ts_df = pd.DataFrame()

    for idx, pwl_ts in enumerate(pwl_dataset):
        end_point = pwl_ts[-1]
        end_point_time = end_point[0]
        ceil_ep_time = np.ceil(end_point_time)

        new_x = np.arange(0, ceil_ep_time, sampling_frequency)

        old_x, y = zip(*pwl_ts)
        interpolator_function = interp1d(old_x, y,
                                         kind="linear",
                                         fill_value="extrapolate")
        # fill_value="extrapolate" very important!
        # If not, because of the ceiling operation, the index would be off range

        new_y = interpolator_function(new_x)

        new_ts = pd.Series(new_y, index=new_x, name=idx)

        ts_df = ts_df.append(new_ts)

    return ts_df


def generate_noisy_ts_dataset(timeseries_df, mu, sigma, seed=True):

    if seed is True:
        np.random.seed(1234)
    elif seed is not False:
        np.random.seed(seed)

    noisy_df = pd.DataFrame()

    for index, row in timeseries_df.iterrows():

        # remove nans
        row = row.dropna()
        noise_vector = np.random.normal(mu, sigma, row.size)

        new_values = np.add(row.values, noise_vector)

        new_ts = pd.Series(new_values, index=row.index, name=index)

        noisy_df = noisy_df.append(new_ts)

    return noisy_df


def save_dataset(dataset, save_to_location):
    """ This function saves a generated dataset """

    with open(save_to_location, 'w') as curr_file:

        if isinstance(dataset, list):
            json.dump(dataset, curr_file)

        elif isinstance(dataset, pd.DataFrame):
            dataset.to_csv(path_or_buf=curr_file, index=False)

        else:
            raise NotImplementedError("We don't have an implementation for that dataset type")


def load_dataset(load_from_location, dataset_type="df"):
    """ This function loads a dataset """

    with open(load_from_location, 'r') as curr_file:

        # list of lists
        if dataset_type == "lol":
            return json.load(curr_file)

        elif dataset_type == "df":
            df = pd.read_csv(curr_file)
            df.columns = pd.to_numeric(df.columns.values)
            return df

        else:
            raise NotImplementedError("We don't have an implementation for that dataset type")
