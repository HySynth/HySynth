from hysynth.utils.hybrid_system.library import construct_hybrid_automaton_name, construct_variable_names
from hysynth.utils.hybrid_system import HybridSystemAffineDynamics


def construct_automaton_from_pwld_function(pwld_sequence, delta_ha, automaton_name=None):
    automaton_name = construct_hybrid_automaton_name(automaton_name)
    variable_names = construct_variable_names(pw_function=pwld_sequence, function_type="pwld")

    automaton = HybridSystemAffineDynamics(name=automaton_name, variable_names=variable_names, delta=delta_ha)

    return automaton
