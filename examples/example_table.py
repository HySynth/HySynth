import random
import numpy as np
from data.synthetic_data.automata_library import two_mode_p1_m1_ha, three_mode_p1_m1_0_ha, four_mode_p2_m1_p1_m2_ha
from hysynth.pwl.simulation import dataset_generation as dgen
from hysynth.pwl.hysynth_pwl import ha_synthesis_from_data_pwl, ha_adaptation_from_data_pwl
from examples.example_synthesis_from_ha_simulations import show_example


def example_ex1():
    # comments: automaton is great, simulations look good
    ha_in = two_mode_p1_m1_ha()
    max_jumps = 10
    time_bound = 10.
    starting_positions_in = {"Q1": [(5, 5)]}
    starting_positions_out = {"Q0": [(5, 5)]}
    time_horizon = 30.
    return ha_in, max_jumps, time_bound, starting_positions_in, starting_positions_out, time_horizon


def example_ex2():
    # comments: automaton is great, simulations look weird
    ha_in = three_mode_p1_m1_0_ha()
    max_jumps = 10
    time_bound = 10.
    starting_positions_in = {"Q1": [(5, 5)]}
    starting_positions_out = {"Q0": [(5, 5)]}
    time_horizon = 20.
    return ha_in, max_jumps, time_bound, starting_positions_in, starting_positions_out, time_horizon


def example_ex3():
    # comments: automaton is great, simulations look weird
    ha_in = four_mode_p2_m1_p1_m2_ha()
    max_jumps = 10
    time_bound = 10.
    starting_positions_in = {"Q1": [(5, 5)]}
    starting_positions_out = {"Q0": [(5, 5)]}
    time_horizon = 20.
    return ha_in, max_jumps, time_bound, starting_positions_in, starting_positions_out, time_horizon


def run_example(ex_number=0):
    if ex_number == 1:
        ex = example_ex1
    elif ex_number == 2:
        ex = example_ex2
    elif ex_number == 3:
        ex = example_ex3
    else:
        print("Please provide a number from {1, 2, 3}!")
        return

    random.seed(1234)
    np.random.seed(1234)
    print("Example", ex_number)
    ha_in, max_jumps, time_bound, starting_positions_in, starting_positions_out, time_horizon = ex()
    ha_in._delta = 0.2  # overwrite delta here to have a global value
    ha_out = None
    for i in [1, 2]:
        if i == 1:
            n_iterations = 10
        elif i == 2:
            n_iterations = 90
        else:
            raise ValueError("iteration {0} not defined".format(i))

        input_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_in,
                                                  n_iterations=n_iterations,
                                                  time_bound=time_bound,
                                                  seed=False,
                                                  starting_positions=starting_positions_in,
                                                  time_horizon=time_horizon)

        # show_example(original_dataset=input_dataset, resulting_dataset=input_dataset)

        if i == 1:
            print("\n\nSOURCE AUTOMATON")
            print(ha_in)
            ha_out = ha_synthesis_from_data_pwl(input_dataset, delta_ha=ha_in.delta, clustering_bandwidth=0.1,
                                                pwl_epsilon=0.0)
        else:
            ha_out = ha_adaptation_from_data_pwl(input_dataset, hybrid_automaton=ha_out, pwl_epsilon=0.0)

        print("\n\nRESULT AUTOMATON ITERATION {0}".format(i))
        print(ha_out)

        resulting_dataset = dgen.generate_pwl_dataset(hybrid_automaton=ha_out,
                                                      n_iterations=10,
                                                      time_bound=time_bound,
                                                      seed=False,
                                                      starting_positions=starting_positions_out,
                                                      time_horizon=time_horizon)

        if i == 2:
            fig = show_example(original_dataset=input_dataset[0:3], resulting_dataset=resulting_dataset[0:3])
            fig.savefig("ex{0}.pdf".format(ex_number))


def main():
    run_example(1)
    run_example(2)
    run_example(3)


if __name__ == "__main__":
    main()
