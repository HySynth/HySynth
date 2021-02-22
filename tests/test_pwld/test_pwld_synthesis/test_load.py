from hysynth.utils.hybrid_system import HybridSystemAffineDynamics, map_initial_condition
from hysynth.utils.sets import Hyperrectangle
from hysynth.pwld import simulate, plot_pwld_functions
from hysynth.pwld.julia_bridge.library import load_julia_libraries


if __name__ == "__main__":
    load_julia_libraries(log=True)
    file_name = "gearbox_original"
    hybrid_automaton_source = HybridSystemAffineDynamics.load(filename=file_name)
    file_name = "gearbox_10"
    hybrid_automaton_synthesized = HybridSystemAffineDynamics.load(filename=file_name)

    n_samples = 10
    max_perturbation = 0.0001
    path_length = 5
    max_dwell_time = 10.0
    time_step = 0.01
    perturbation_ignored = 1
    initial_condition = {"q1": Hyperrectangle([27.0, 0.0], [1.0, 1e-9])}
    initial_condition_new = map_initial_condition(old_initial_condition=initial_condition,
                                                  old_automaton=hybrid_automaton_source,
                                                  new_automaton=hybrid_automaton_synthesized)
    n_simulations = 5

    simulations = simulate(hybrid_automaton=hybrid_automaton_synthesized,
                           initial_condition=initial_condition_new, max_dwell_time=max_dwell_time,
                           n_samples=n_simulations, max_perturbation=max_perturbation, path_length=path_length,
                           perturbation_ignored=perturbation_ignored, time_step=time_step)
    plot_pwld_functions(simulations, file_name="test.pdf")
