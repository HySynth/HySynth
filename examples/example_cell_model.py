from functools import partial

import matplotlib.pyplot as plt

from data.synthetic_data.cell_model import cell_model_ha
from hysynth.pwl.simulation import dataset_generation as dgen
from hysynth import ha_synthesis_from_data_pwl, ha_adaptation_from_data_pwl
from examples.example_synthesis_from_ha_simulations import show_example


def example_cell():
    ha_in = cell_model_ha()
    max_jumps = 10
    time_bound = 100.
    n_iterations = 50

    input_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_in,
                                              n_iterations=n_iterations,
                                              max_jumps=max_jumps,
                                              time_bound=time_bound)

    ha_out = ha_synthesis_from_data_pwl(input_dataset, delta_ha=ha_in.delta, clustering_bandwidth=0.1)

    resulting_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_out,
                                                  n_iterations=n_iterations,
                                                  max_jumps=max_jumps,
                                                  time_bound=time_bound)

    print(ha_in)
    print("\n\n\n\n")
    print(ha_out)

    show_example(original_dataset=input_dataset, resulting_dataset=resulting_dataset)


def example_cell_with_noise():
    ha_in = cell_model_ha()
    max_jumps = 50
    time_bound = 100.
    n_iterations = 10

    input_pwl_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_in,
                                                  n_iterations=n_iterations,
                                                  max_jumps=max_jumps,
                                                  time_bound=time_bound)

    ts_dataset = dgen.generate_timeseries_dataset(input_pwl_dataset, sampling_frequency=1)

    noisy_ts_dataset = dgen.generate_noisy_ts_dataset(ts_dataset, mu=0, sigma=0.5, seed=1234)

    # show_example(input_pwl_dataset, noisy_ts_dataset, title1="Clean data", title2="Noisy data")

    ha_out = ha_synthesis_from_data_pwl(noisy_ts_dataset,
                                        delta_ha=6,
                                        clustering_bandwidth=10,
                                        pwl_epsilon=5)

    resulting_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_out,
                                                  n_iterations=n_iterations,
                                                  max_jumps=max_jumps,
                                                  time_bound=time_bound)

    print(ha_in)
    print("\n\n\n\n")
    print(ha_out)

    show_example(original_dataset=noisy_ts_dataset, resulting_dataset=resulting_dataset)


def example_cell_noise_with_full_automaton_input():
    """ Here we try and input the automaton from which the data was generated """

    ha_in = cell_model_ha()
    max_jumps = 20
    time_bound = 100.
    n_iterations = 5

    input_pwl_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_in,
                                                  n_iterations=n_iterations,
                                                  max_jumps=max_jumps,
                                                  time_bound=time_bound)

    ts_dataset = dgen.generate_timeseries_dataset(input_pwl_dataset, sampling_frequency=1)

    noisy_ts_dataset = dgen.generate_noisy_ts_dataset(ts_dataset, mu=0, sigma=1, seed=1234)

    show_example(input_pwl_dataset, noisy_ts_dataset, title1="Clean data", title2="Noisy data")

    ha_in._delta = 5.0

    ha_out = ha_adaptation_from_data_pwl(data=noisy_ts_dataset,
                                         hybrid_automaton=ha_in,
                                         pwl_epsilon=4)

    resulting_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_out,
                                                  n_iterations=n_iterations,
                                                  max_jumps=max_jumps,
                                                  time_bound=time_bound)

    print(ha_in)
    print("\n\n\n\n")
    print(ha_out)

    show_example(original_dataset=noisy_ts_dataset, resulting_dataset=resulting_dataset)


def create_cell_dataset(max_jumps=10, n_iterations=5):
    """ In this function we create a bigger cell dataset which we then save and work with """
    ha_in = cell_model_ha()
    time_bound = 100.

    created_pwl_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_in,
                                                    n_iterations=n_iterations,
                                                    max_jumps=max_jumps,
                                                    time_bound=time_bound)

    dataset_save_loc = "data/synthetic_data/cell_datasets/cell_dset_n{}_mj{}.csv".format(n_iterations, max_jumps)
    dgen.save_dataset(save_to_location=dataset_save_loc, dataset=created_pwl_dataset)


def example_cell_run_on_dset():

    dset_name = "cell_dset_n{}_mj{}.csv".format(50, 10)
    input_dataset = dgen.load_dataset(load_from_location="data/synthetic_data/cell_datasets/{}".format(dset_name),
                                      dataset_type="lol")

    ha_out_d005 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=0.05, clustering_bandwidth=0.1)
    ha_out_d01 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=0.1, clustering_bandwidth=0.1)
    ha_out_d04 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=0.4, clustering_bandwidth=0.1)
    ha_out_d07 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=0.7, clustering_bandwidth=0.1)
    ha_out_d1 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=1, clustering_bandwidth=0.1)

    make_simulations = partial(dgen.generate_pwl_dataset, n_iterations=20, max_jumps=20, time_bound=100.)

    sim_dset_d005 = make_simulations(hybrid_automaton=ha_out_d005)

    sim_dset_d01 = make_simulations(hybrid_automaton=ha_out_d01)

    sim_dset_d04 = make_simulations(hybrid_automaton=ha_out_d04)

    sim_dset_d07 = make_simulations(hybrid_automaton=ha_out_d07)

    sim_dset_d1 = make_simulations(hybrid_automaton=ha_out_d1)

    # make the figure
    fig, axes = plt.subplots(nrows=6)

    datasets_dict = {"Original Data": input_dataset,
                     "Simulated dataset with delta: 0.05": sim_dset_d005,
                     "Simulated dataset with delta: 0.1": sim_dset_d01,
                     "Simulated dataset with delta: 0.4": sim_dset_d04,
                     "Simulated dataset with delta: 0.7": sim_dset_d07,
                     "Simulated dataset with delta: 1. ": sim_dset_d1}

    # loop over the datasets
    for i, (dset_name, dset_data) in enumerate(datasets_dict.items()):
        current_ax = axes[i]

        for pwl_simulation in dset_data:
            x, y = zip(*pwl_simulation)
            current_ax.plot(x, y)

        current_ax.set_title(dset_name)

    plt.show()


def example_cell_run_on_dset_bigger_ranges():

    dset_name = "cell_dset_n{}_mj{}.csv".format(50, 10)
    input_dataset = dgen.load_dataset(load_from_location="data/synthetic_data/cell_datasets/{}".format(dset_name),
                                      dataset_type="lol")

    ha_out_d1 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=1, clustering_bandwidth=0.1)
    ha_out_d5 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=5, clustering_bandwidth=0.1)
    ha_out_d8 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=8, clustering_bandwidth=0.1)
    ha_out_d12 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=12, clustering_bandwidth=0.1)
    ha_out_d15 = ha_synthesis_from_data_pwl(input_dataset, delta_ha=15, clustering_bandwidth=0.1)

    make_simulations = partial(dgen.generate_pwl_dataset, n_iterations=20, max_jumps=20, time_bound=100.)

    sim_dset_d1 = make_simulations(hybrid_automaton=ha_out_d1)

    sim_dset_d5 = make_simulations(hybrid_automaton=ha_out_d5)

    sim_dset_d8 = make_simulations(hybrid_automaton=ha_out_d8)

    sim_dset_d12 = make_simulations(hybrid_automaton=ha_out_d12)

    sim_dset_d15 = make_simulations(hybrid_automaton=ha_out_d15)

    # make the figure
    fig, axes = plt.subplots(nrows=6)

    datasets_dict = {"Original Data": input_dataset,
                     "Simulated dataset with delta: 1": sim_dset_d1,
                     "Simulated dataset with delta: 5": sim_dset_d5,
                     "Simulated dataset with delta: 8": sim_dset_d8,
                     "Simulated dataset with delta: 12": sim_dset_d12,
                     "Simulated dataset with delta: 15": sim_dset_d15}

    # loop over the datasets
    for i, (dset_name, dset_data) in enumerate(datasets_dict.items()):
        current_ax = axes[i]

        for pwl_simulation in dset_data:
            x, y = zip(*pwl_simulation)
            current_ax.plot(x, y)

        current_ax.set_title(dset_name)

    plt.show()


def example_cell_plot_for_paper():
    ha_in = cell_model_ha()
    max_jumps = 30
    time_bound = 100.
    n_iterations = 50
    init_range = [(-75.5, -74.5)]

    initial_spec = {"R": init_range}

    input_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_in,
                                              n_iterations=n_iterations,
                                              max_jumps=max_jumps,
                                              time_bound=time_bound,
                                              starting_positions=initial_spec)

    ha_out = ha_synthesis_from_data_pwl(input_dataset, delta_ha=ha_in.delta, clustering_bandwidth=0.1)

    initial_spec_res = {"Q0": init_range}

    resulting_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_out,
                                                  n_iterations=n_iterations,
                                                  max_jumps=max_jumps,
                                                  time_bound=time_bound,
                                                  starting_positions=initial_spec_res,
                                                  seed=6574)

    print(ha_out)

    sorted_input_dset = sorted(input_dataset, key=lambda x: len(x), reverse=True)

    fig1 = plt.figure(figsize=plt.figaspect(0.3))
    ax1, ax2 = fig1.subplots(ncols=2)

    for i in range(0, 3):
        x, y = zip(*sorted_input_dset[i])
        ax1.plot(x, y)
        ax1.set(title='Original Dataset',
                ylabel='voltage (mV)',
                xlabel='time (ms)',
                xlim=[0, 500])
        ax1.title.set_fontsize(20)
        for item in ([ax1.xaxis.label, ax1.yaxis.label] +
                     ax1.get_xticklabels() + ax1.get_yticklabels()):
            item.set_fontsize(16)

    # fig1.tight_layout()
    # plt.show()
    # fig1.savefig("examples/figures/original.pdf")

    sorted_res_dset = sorted(resulting_dataset, key=lambda x: len(x), reverse=True)

    # fig2 = plt.figure(figsize=plt.figaspect(0.3))
    # ax2 = fig2.subplots()

    for i in range(0, 3):
        x, y = zip(*sorted_res_dset[i])
        ax2.plot(x, y)
        ax2.set(title='Simulated Dataset',
                xlabel='time (ms)',
                xlim=[0, 500]
                )
        ax2.title.set_fontsize(20)
        for item in ([ax2.xaxis.label, ax2.yaxis.label] +
                     ax2.get_xticklabels() + ax2.get_yticklabels()):
            item.set_fontsize(16)

    fig1.tight_layout(w_pad=5)
    plt.show()
    fig1.savefig("cell_plots.pdf")


def main():
    example_cell_with_noise()


if __name__ == "__main__":
    main()
