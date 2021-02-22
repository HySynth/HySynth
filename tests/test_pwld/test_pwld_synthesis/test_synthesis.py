import pytest
from pathlib import Path

from hysynth.utils.hybrid_system import HybridSystemAffineDynamics
from hysynth.utils.dynamics import *
from hysynth.pwld import construct_automaton_from_pwld_function, sample_trajectory_pwld, imitate_hybrid_automaton_pwld,\
    ha_synthesis_from_pwld_functions, time_series2pwld_function
from hysynth.pwld.julia_bridge.library import load_julia_libraries, reset_seed, set_flow, BallInf_jl,\
    Hyperrectangle_jl, HalfSpace_jl, HPolyhedron_jl
from data.real_data.preprocess import data2array as load_time_series
from hysynth.pwld.plot import plot_pwld_functions_and_time_series


def pwld_function_1():
    A1 = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    T1 = 1.0
    x0 = [1.0, 1.0]
    epsilon = 0.0
    return [(A1, T1)], x0, epsilon


def pwld_function_2():
    A1 = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    T1 = 1.0
    A2 = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    T2 = 2.0
    x0 = [1.0, 1.0]
    epsilon = 0.0
    return [(A1, T1), (A2, T2)], x0, epsilon


def pwld_function_3():
    A1 = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    T1 = 1.0
    A2 = LinDyn([[0.0, 1.0], [1.0, 0.0]])
    T2 = 2.0
    A3 = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    T3 = 3.0
    A4 = LinDyn([[0.0, 1.0], [1.0, 0.0]])
    T4 = 4.0
    x0 = [1.0, 1.0]
    epsilon = 0.0
    return [(A1, T1), (A2, T2), (A3, T3), (A4, T4)], x0, epsilon


@pytest.fixture()
def pwld_function_test():
    return pwld_function_1()


def time_series_ekg():
    path = Path(__file__).parent.parent.parent.parent / "data" / "real_data" / "datasets" / "ekg_data"
    filename1 = path / "ekg_1.csv"
    filename2 = path / "ekg_2.csv"
    filename3 = path / "ekg_3.csv"
    f1 = load_time_series(filename1, 2)
    f2 = load_time_series(filename2, 2)
    f3 = load_time_series(filename3, 2)
    dataset = [f1, f2, f3]
    return dataset


def hybrid_automaton_thermostat_linear():
    ha = HybridSystemAffineDynamics(name="HA Thermostat linear", variable_names=["x", "c"], delta=0.1)

    load_julia_libraries()

    a = 0.1

    ha.add_location("off")
    A = LinDyn([[-a, 0.0], [0.0, 0.0]])
    set_flow(ha, "off", A)
    inv = Hyperrectangle_jl([20.0, 1.0], [2.0, 1e-9])
    ha.set_invariant("off", inv)

    ha.add_location("on")
    A = LinDyn([[-a, 30.0 * a], [0.0, 0.0]])
    set_flow(ha, "on", A)
    ha.set_invariant("on", inv)

    ha.add_edge("off", "on")
    guard = Hyperrectangle_jl([18.5, 1.0], [0.5, 1e-9])
    ha.set_guard(("off", "on"), guard)

    ha.add_edge("on", "off")
    guard = Hyperrectangle_jl([21.5, 1.0], [0.5, 1e-9])
    ha.set_guard(("on", "off"), guard)

    return ha


def hybrid_automaton_thermostat_affine():
    ha = HybridSystemAffineDynamics(name="HA Thermostat affine", variable_names=["x"], delta=0.1)

    load_julia_libraries()

    a = 0.1

    ha.add_location("off")
    A = LinDyn([[-a]])
    set_flow(ha, "off", A)
    inv = Hyperrectangle_jl([20.0], [2.0])
    ha.set_invariant("off", inv)

    ha.add_location("on")
    A = AffDyn([[-a]], [30.0 * a])
    set_flow(ha, "on", A)
    ha.set_invariant("on", inv)

    ha.add_edge("off", "on")
    guard = Hyperrectangle_jl([18.5], [0.5])
    ha.set_guard(("off", "on"), guard)

    ha.add_edge("on", "off")
    guard = Hyperrectangle_jl([21.5], [0.5])
    ha.set_guard(("on", "off"), guard)

    return ha


def hybrid_automaton_linear_switching():
    # see https://ths.rwth-aachen.de/research/projects/hypro/5-dimensional-switching-linear-system/
    ha = HybridSystemAffineDynamics(name="HA Linear switching",
                                    variable_names=["x{:d}".format(i) for i in range(1, 6)],
                                    delta=0.1)

    load_julia_libraries()

    a_geq = [-1.0, 0.0, 0.0, 0.0, 0.0]
    a_leq = [1.0, 0.0, 0.0, 0.0, 0.0]
    eps = 0.1  # bloating of hyperplanar guards to make simulation find them

    loc1 = "loc1"
    ha.add_location(loc1)
    A1 = LinDyn([[-0.8047, 8.7420, -2.4591, -8.2714, -1.8640],
                 [-8.6329, -0.5860, -2.1006, 3.6035, -1.8423],
                 [2.4511, 2.2394, -0.7538, -3.6934, 2.4585],
                 [8.3858, -3.1739, 3.7822, -0.6249, 1.8829],
                 [1.8302, 1.9869, -2.4539, -1.7726, -0.7911]])
    set_flow(ha, loc1, A1)
    inv = HalfSpace_jl(a_geq, -3.0)  # x1 >= 3
    ha.set_invariant(loc1, inv)

    loc2 = "loc2"
    ha.add_location(loc2)
    A2 = LinDyn([[-0.8316, 8.7658, -2.4744, -8.2608, -1.9033],
                 [-0.8316, -0.5860, -2.1006, 3.6035, -1.8423],
                 [2.4511, 2.2394, -0.7538, -3.6934, 2.4585],
                 [8.3858, -3.1739, 3.7822, -0.6249, 1.8829],
                 [1.5964, 2.1936, -2.5872, -1.6812, -1.1324]])
    set_flow(ha, loc2, A2)
    inv = HalfSpace_jl(a_geq, -2.0)  # x1 >= 2
    ha.set_invariant(loc2, inv)

    loc3 = "loc3"
    ha.add_location(loc3)
    A3 = LinDyn([[-0.9275, 8.8628, -2.5428, -8.2329, -2.0324],
                 [-0.8316, -0.5860, -2.1006, 3.6035, -1.8423],
                 [2.4511, 2.2394, -0.7538, -3.6934, 2.4585],
                 [8.3858, -3.1739, 3.7822, -0.6249, 1.8829],
                 [0.7635, 3.0357, -3.1814, -1.4388, -2.2538]])
    set_flow(ha, loc3, A3)
    inv = HalfSpace_jl(a_geq, -1.0)  # x1 >= 1
    ha.set_invariant(loc3, inv)

    loc4 = "loc4"
    ha.add_location(loc4)
    A4 = LinDyn([[-1.4021, 10.1647, -3.3937, -8.5139, -2.9602],
                 [-0.8316, -0.5860, -2.1006, 3.6035, -1.8423],
                 [2.4511, 2.2394, -0.7538, -3.6934, 2.4585],
                 [8.3858, -3.1739, 3.7822, -0.6249, 1.8829],
                 [-3.3585, 14.3426, -10.5703, -3.8785, -10.3111]])
    set_flow(ha, loc4, A4)
    inv = HalfSpace_jl(a_geq, 0.0)  # x1 >= 0
    ha.set_invariant(loc4, inv)

    loc5 = "loc5"
    ha.add_location(loc5)
    set_flow(ha, loc5, A4)  # same dynamics as loc4
    inv = HalfSpace_jl(a_leq, 1.0)  # x1 <= 1
    ha.set_invariant(loc5, inv)

    ha.add_edge(loc1, loc2)
    b = 3.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_leq, b + eps), HalfSpace_jl(a_geq, -b + eps)])
    ha.set_guard((loc1, loc2), guard)

    ha.add_edge(loc2, loc3)
    b = 2.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_leq, b + eps), HalfSpace_jl(a_geq, -b + eps)])
    ha.set_guard((loc2, loc3), guard)

    ha.add_edge(loc3, loc4)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_leq, b + eps), HalfSpace_jl(a_geq, -b + eps)])
    ha.set_guard((loc3, loc4), guard)

    ha.add_edge(loc4, loc5)
    b = 0.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_leq, b + eps), HalfSpace_jl(a_geq, -b + eps)])
    ha.set_guard((loc4, loc5), guard)

    ha.add_edge(loc5, loc1)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_leq, b + eps), HalfSpace_jl(a_geq, -b + eps)])
    ha.set_guard((loc5, loc1), guard)

    return ha


def hybrid_automaton_two_tanks_linear():
    # see https://ths.rwth-aachen.de/research/projects/hypro/two-tank/
    ha = HybridSystemAffineDynamics(name="HA Two tanks linear", variable_names=["x1", "x2", "c"], delta=0.1)

    load_julia_libraries()

    a_x1_leq = [1.0, 0.0, 0.0]
    a_x1_geq = [-1.0, 0.0, 0.0]
    a_x2_leq = [0.0, 1.0, 0.0]
    a_x2_geq = [0.0, -1.0, 0.0]
    eps = 0.1  # bloating of hyperplanar guards to make simulation find them

    off_off = "off_off"
    ha.add_location(off_off)
    A1 = LinDyn([[-1.0, 0.0, -2.0],
                 [1.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0]])
    set_flow(ha, off_off, A1)
    inv = HPolyhedron_jl([HalfSpace_jl(a_x1_geq, 1.0), HalfSpace_jl(a_x2_leq, 1.0)])  # x1 >= -1 & x2 <= 1
    ha.set_invariant(off_off, inv)

    on_off = "on_off"
    ha.add_location(on_off)
    A2 = LinDyn([[-1.0, 0.0, 3.0],
                 [1.0, 0.0, 0.0],
                 [0.0, 0.0, 0.0]])
    set_flow(ha, on_off, A2)
    inv = HalfSpace_jl(a_x2_leq, 1.0)  # x2 <= 1
    ha.set_invariant(on_off, inv)

    off_on = "off_on"
    ha.add_location(off_on)
    A3 = LinDyn([[-1.0, 0.0, -2.0],
                 [1.0, -1.0, -5.0],
                 [0.0, 0.0, 0.0]])
    set_flow(ha, off_on, A3)
    inv = HPolyhedron_jl([HalfSpace_jl(a_x1_geq, 1.0), HalfSpace_jl(a_x2_geq, 0.0)])  # x1 >= -1 & x2 >= 0
    ha.set_invariant(off_on, inv)

    on_on = "on_on"
    ha.add_location(on_on)
    A4 = LinDyn([[-1.0, 0.0, 3.0],
                 [1.0, -1.0, -5.0],
                 [0.0, 0.0, 0.0]])
    set_flow(ha, on_on, A4)
    inv = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, 1.0), HalfSpace_jl(a_x2_geq, 0.0)])  # x1 <= 1 & x2 >= 0
    ha.set_invariant(on_on, inv)

    ha.add_edge(off_off, on_off)
    b = -1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, b + eps),
                            HalfSpace_jl(a_x1_geq, -b + eps)])  # x1 = -1
    ha.set_guard((off_off, on_off), guard)

    ha.add_edge(off_off, off_on)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 1
    ha.set_guard((off_off, off_on), guard)

    ha.add_edge(on_off, off_on)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 1
    ha.set_guard((on_off, off_on), guard)

    ha.add_edge(off_on, off_off)
    b = 0.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 0
    ha.set_guard((off_on, off_off), guard)

    ha.add_edge(off_on, on_on)
    b = -1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, b + eps),
                            HalfSpace_jl(a_x1_geq, -b + eps)])  # x1 = -1
    ha.set_guard((off_on, on_on), guard)

    ha.add_edge(on_on, on_off)
    b = 0.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 0
    ha.set_guard((on_on, on_off), guard)

    ha.add_edge(on_on, off_on)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, b + eps),
                            HalfSpace_jl(a_x1_geq, -b + eps)])  # x1 = 1
    ha.set_guard((on_on, off_on), guard)

    return ha


def hybrid_automaton_two_tanks_affine():
    # see https://ths.rwth-aachen.de/research/projects/hypro/two-tank/
    ha = HybridSystemAffineDynamics(name="HA Two tanks affine", variable_names=["x1", "x2"], delta=0.1)

    load_julia_libraries()

    a_x1_leq = [1.0, 0.0]
    a_x1_geq = [-1.0, 0.0]
    a_x2_leq = [0.0, 1.0]
    a_x2_geq = [0.0, -1.0]
    eps = 0.1  # bloating of hyperplanar guards to make simulation find them

    off_off = "off_off"
    ha.add_location(off_off)
    A1 = AffDyn([[-1.0, 0.0],
                 [1.0, 0.0],
                 [0.0, 0.0]], [-2.0, 0.0])
    set_flow(ha, off_off, A1)
    inv = HPolyhedron_jl([HalfSpace_jl(a_x1_geq, 1.0), HalfSpace_jl(a_x2_leq, 1.0)])  # x1 >= -1 & x2 <= 1
    ha.set_invariant(off_off, inv)

    on_off = "on_off"
    ha.add_location(on_off)
    A2 = AffDyn([[-1.0, 0.0],
                 [1.0, 0.0],
                 [0.0, 0.0]], [3.0, 0.0])
    set_flow(ha, on_off, A2)
    inv = HalfSpace_jl(a_x2_leq, 1.0)  # x2 <= 1
    ha.set_invariant(on_off, inv)

    off_on = "off_on"
    ha.add_location(off_on)
    A3 = AffDyn([[-1.0, 0.0],
                 [1.0, -1.0],
                 [0.0, 0.0]], [-2.0, -5.0])
    set_flow(ha, off_on, A3)
    inv = HPolyhedron_jl([HalfSpace_jl(a_x1_geq, 1.0), HalfSpace_jl(a_x2_geq, 0.0)])  # x1 >= -1 & x2 >= 0
    ha.set_invariant(off_on, inv)

    on_on = "on_on"
    ha.add_location(on_on)
    A4 = AffDyn([[-1.0, 0.0],
                 [1.0, -1.0],
                 [0.0, 0.0]], [3.0, -5.0])
    set_flow(ha, on_on, A4)
    inv = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, 1.0), HalfSpace_jl(a_x2_geq, 0.0)])  # x1 <= 1 & x2 >= 0
    ha.set_invariant(on_on, inv)

    ha.add_edge(off_off, on_off)
    b = -1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, b + eps),
                            HalfSpace_jl(a_x1_geq, -b + eps)])  # x1 = -1
    ha.set_guard((off_off, on_off), guard)

    ha.add_edge(off_off, off_on)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 1
    ha.set_guard((off_off, off_on), guard)

    ha.add_edge(on_off, off_on)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 1
    ha.set_guard((on_off, off_on), guard)

    ha.add_edge(off_on, off_off)
    b = 0.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 0
    ha.set_guard((off_on, off_off), guard)

    ha.add_edge(off_on, on_on)
    b = -1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, b + eps),
                            HalfSpace_jl(a_x1_geq, -b + eps)])  # x1 = -1
    ha.set_guard((off_on, on_on), guard)

    ha.add_edge(on_on, on_off)
    b = 0.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x2_leq, b + eps),
                            HalfSpace_jl(a_x2_geq, -b + eps)])  # x2 = 0
    ha.set_guard((on_on, on_off), guard)

    ha.add_edge(on_on, off_on)
    b = 1.0
    guard = HPolyhedron_jl([HalfSpace_jl(a_x1_leq, b + eps),
                            HalfSpace_jl(a_x1_geq, -b + eps)])  # x1 = 1
    ha.set_guard((on_on, off_on), guard)

    return ha


def hybrid_automaton_gearbox():
    # see "An Algorithmic Approach to Global Asymptotic Stability Verification of Hybrid Systems"
    # note: bug in paper: all omegas need to be swapped in the guards and also in the invariant of q1
    ha = HybridSystemAffineDynamics(name="HA Gearbox", variable_names=["v", "T_I"], delta=0.1)

    load_julia_libraries()

    M = 1500.0
    T = 40.0
    omega_l = 500.0
    omega_h = 230.0
    p1 = 50.0
    p2 = 32.0
    p3 = 20.0
    p4 = 14.0
    k1 = float(15/4)
    k2 = float(375/64)
    k3 = float(75/8)
    k4 = float(375/28)
    vd = 30.0

    a_v_leq = [1.0, 0.0]
    a_v_geq = [-1.0, 0.0]
    eps = 0.1  # bloating of hyperplanar guards to make simulation find them

    q1 = "q1"
    ha.add_location(q1)
    A1 = LinDyn([[-p1 * k1 / M, -p1 / M],
                 [k1 / T, 0.0]])
    set_flow(ha, q1, A1)
    inv = HalfSpace_jl(a_v_geq, -vd + 1/p1 * omega_l + eps)  # v >= vd - 1/p1 * omega_l  (bug!)
    ha.set_invariant(q1, inv)

    q2 = "q2"
    ha.add_location(q2)
    A2 = LinDyn([[-p2 * k2 / M, -p2 / M],
                 [k2 / T, 0.0]])
    set_flow(ha, q2, A2)
    inv = HPolyhedron_jl([HalfSpace_jl(a_v_geq, -vd + 1/p2 * omega_l + eps),  # v >= vd - 1/p2 * omega_l
                          HalfSpace_jl(a_v_leq, vd - 1/p2 * omega_h + eps)])  # v <= vd - 1/p2 * omega_h
    ha.set_invariant(q2, inv)

    q3 = "q3"
    ha.add_location(q3)
    A3 = LinDyn([[-p3 * k3 / M, -p3 / M],
                 [k3 / T, 0.0]])
    set_flow(ha, q3, A3)
    inv = HPolyhedron_jl([HalfSpace_jl(a_v_geq, -vd + 1/p3 * omega_l + eps),  # v >= vd - 1/p3 * omega_l
                          HalfSpace_jl(a_v_leq, vd - 1/p3 * omega_h + eps)])  # v <= vd - 1/p3 * omega_h
    ha.set_invariant(q3, inv)

    q4 = "q4"
    ha.add_location(q4)
    A4 = LinDyn([[-p4 * k4 / M, -p4 / M],
                 [k4 / T, 0.0]])
    set_flow(ha, q4, A4)
    inv = HalfSpace_jl(a_v_leq, vd - 1/p4 * omega_h + eps)  # v <= vd - 1/p4 * omega_l
    ha.set_invariant(q4, inv)

    ha.add_edge(q1, q2)
    b = vd - 1/p1 * omega_l  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p1 * omega_l
    ha.set_guard((q1, q2), guard)

    ha.add_edge(q2, q1)
    b = vd - 1/p2 * omega_h  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p2 * omega_h
    ha.set_guard((q2, q1), guard)

    ha.add_edge(q2, q3)
    b = vd - 1/p2 * omega_l  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p2 * omega_l
    ha.set_guard((q2, q3), guard)

    ha.add_edge(q3, q2)
    b = vd - 1/p3 * omega_h  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p3 * omega_h
    ha.set_guard((q3, q2), guard)

    ha.add_edge(q3, q4)
    b = vd - 1/p3 * omega_l  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p3 * omega_l
    ha.set_guard((q3, q4), guard)

    ha.add_edge(q4, q3)
    b = vd - 1/p4 * omega_h  # bug!
    guard = HPolyhedron_jl([HalfSpace_jl(a_v_leq, b + eps),
                            HalfSpace_jl(a_v_geq, -b + eps)])  # v = vd - 1/p4 * omega_h
    ha.set_guard((q4, q3), guard)

    return ha


def hybrid_automaton_1():
    dim = 2
    ha = HybridSystemAffineDynamics(name="HA 1",
                                    variable_names=["x{:d}".format(i) for i in range(dim)],
                                    delta=0.1)

    load_julia_libraries()

    ha.add_location("loc1")
    A = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    set_flow(ha, "loc1", A)
    inv = BallInf_jl([0.0, 0.0], 5.0)
    ha.set_invariant("loc1", inv)

    ha.add_location("loc2")
    A = LinDyn([[0.0, 1.0], [-1.0, 0.0]])
    set_flow(ha, "loc2", A)
    inv = BallInf_jl([0.0, 0.0], 5.0)
    ha.set_invariant("loc2", inv)

    ha.add_edge("loc1", "loc2")
    guard = BallInf_jl([1.0, 0.0], 0.5)
    ha.set_guard(("loc1", "loc2"), guard)

    ha.add_edge("loc2", "loc1")
    guard = BallInf_jl([-1.0, 0.0], 0.5)
    ha.set_guard(("loc2", "loc1"), guard)

    return ha


@pytest.fixture()
def hybrid_automaton_test():
    return hybrid_automaton_thermostat_linear()


def test_initial_construction(pwld_function_test, delta_ha=0.5):
    pwld_sequence, x0, epsilon = pwld_function_test
    ha = construct_automaton_from_pwld_function(pwld_sequence=pwld_sequence, delta_ha=delta_ha)
    assert True


def test_synthesis(pwld_functions, delta_ha=0.5, n_discrete_steps=10, refinement_distance=0.001,
                   reachability_time_step=1e-3, log=1):
    ha = ha_synthesis_from_pwld_functions(data=pwld_functions, delta_ha=delta_ha, n_discrete_steps=n_discrete_steps,
                                          refinement_distance=refinement_distance, print_intermediate=[10],
                                          reachability_time_step=reachability_time_step, log=log)
    print("Result:", ha)
    assert True


def test_simulation(hybrid_automaton, path_length=10, max_dwell_time=5.0, time_step=0.05, max_perturbation=0.01,
                    n_trajectories=10, initial_condition=None):
    for i in range(n_trajectories):
        trajectory = sample_trajectory_pwld(hybrid_automaton=hybrid_automaton,
                                            path_length=path_length, max_dwell_time=max_dwell_time,
                                            time_step=time_step, initial_condition=initial_condition,
                                            max_perturbation=max_perturbation)
        print("trajectory:", trajectory)
    assert True


def test_imitation_thermostat(hybrid_automaton):
    n_samples = 100
    path_length = 5
    max_dwell_time = 7.0
    time_step = 0.05
    n_discrete_steps = 10
    refinement_distance = 1e-3
    reachability_time_step = 1e-3
    max_perturbation = 0.001
    perturbation_ignored = 1
    initial_condition = None
    print_intermediate = [10]
    log = 0

    ha = imitate_hybrid_automaton_pwld(hybrid_automaton=hybrid_automaton, delta_ha=hybrid_automaton.delta,
                                       n_samples=n_samples, path_length=path_length, max_dwell_time=max_dwell_time,
                                       time_step=time_step, n_discrete_steps=n_discrete_steps,
                                       refinement_distance=refinement_distance,
                                       reachability_time_step=reachability_time_step,
                                       initial_condition=initial_condition, max_perturbation=max_perturbation,
                                       perturbation_ignored=perturbation_ignored, print_intermediate=print_intermediate,
                                       log=log)
    print("Original:", hybrid_automaton)
    print("Synthesized:", ha)
    assert True


def test_imitation_linear_switching(hybrid_automaton):
    n_samples = 3
    path_length = 10
    max_dwell_time = 1.0
    time_step = 0.05
    n_discrete_steps = 10
    refinement_distance = 1e-3
    reachability_time_step = 1e-3
    max_perturbation = 0.0
    perturbation_ignored = 1
    initial_set = BallInf_jl([3.1, 4.0, 0.0, 0.0, 0.0], 1e-9)
    initial_condition = {"loc1": initial_set, "loc2": initial_set, "loc3": initial_set, "loc4": initial_set,
                         "loc5": initial_set}
    print_intermediate = [10]
    log = 1

    ha = imitate_hybrid_automaton_pwld(hybrid_automaton=hybrid_automaton, delta_ha=hybrid_automaton.delta,
                                       n_samples=n_samples, path_length=path_length, max_dwell_time=max_dwell_time,
                                       time_step=time_step, n_discrete_steps=n_discrete_steps,
                                       refinement_distance=refinement_distance,
                                       reachability_time_step=reachability_time_step,
                                       initial_condition=initial_condition, max_perturbation=max_perturbation,
                                       perturbation_ignored=perturbation_ignored, print_intermediate=print_intermediate,
                                       log=log)
    print("Original:", hybrid_automaton)
    print("Synthesized:", ha)
    assert True


def test_imitation_two_tanks(hybrid_automaton):
    n_samples = 1
    path_length = 5
    max_dwell_time = 5.0
    time_step = 0.01
    n_discrete_steps = 20
    refinement_distance = 1e-4
    reachability_time_step = 1e-4
    max_perturbation = 0.0
    perturbation_ignored = 1
    is_linear = hybrid_automaton.get_flow("off_off").dim() == 3
    box = Hyperrectangle_jl([2.0, 0.1, 1.0], [0.5, 1e-9, 1e-9]) if is_linear else\
        Hyperrectangle_jl([2.0, 0.1], [0.5, 1e-9])
    initial_condition = {"off_off": box}
    print_intermediate = [10]
    log = 1

    ha = imitate_hybrid_automaton_pwld(hybrid_automaton=hybrid_automaton, delta_ha=hybrid_automaton.delta,
                                       n_samples=n_samples, path_length=path_length, max_dwell_time=max_dwell_time,
                                       time_step=time_step, n_discrete_steps=n_discrete_steps,
                                       refinement_distance=refinement_distance,
                                       reachability_time_step=reachability_time_step,
                                       initial_condition=initial_condition, max_perturbation=max_perturbation,
                                       perturbation_ignored=perturbation_ignored, print_intermediate=print_intermediate,
                                       log=log)
    print("Original:", hybrid_automaton)
    print("Synthesized:", ha)
    assert True


def test_imitation_gearbox(hybrid_automaton):
    n_samples = 10
    path_length = 5
    max_dwell_time = 10.0
    time_step = 0.01
    n_discrete_steps = 10
    refinement_distance = 1e-3
    reachability_time_step = 1e-3
    max_perturbation = 0.0001
    perturbation_ignored = 1
    initial_condition = {"q1": Hyperrectangle_jl([27.0, 0.0], [1.0, 1e-9]),
                         # "q4": Hyperrectangle_jl([-3.0, 0.0], [2.0, 1e-9])
                         }
    print_intermediate = [10]
    log = 1

    print("Original:", hybrid_automaton)
    ha = imitate_hybrid_automaton_pwld(hybrid_automaton=hybrid_automaton, delta_ha=hybrid_automaton.delta,
                                       n_samples=n_samples, path_length=path_length, max_dwell_time=max_dwell_time,
                                       time_step=time_step, n_discrete_steps=n_discrete_steps,
                                       refinement_distance=refinement_distance,
                                       reachability_time_step=reachability_time_step,
                                       initial_condition=initial_condition, max_perturbation=max_perturbation,
                                       perturbation_ignored=perturbation_ignored, print_intermediate=print_intermediate,
                                       log=log)
    print("Original:", hybrid_automaton)
    print("Synthesized:", ha)
    assert True


def test_synthesis_from_time_series(time_series):
    delta_ts = 0.02
    delta_ha = 0.1
    n_discrete_steps = 10
    refinement_distance = 0.001
    reachability_time_step = 1e-3
    print_intermediate = [1, 2]
    log = 1
    pwld_functions = [time_series2pwld_function(ts, delta_ts, log=log) for ts in time_series]
    plot_pwld_functions_and_time_series(pwld_functions, time_series)
    ha = ha_synthesis_from_pwld_functions(data=pwld_functions, delta_ha=delta_ha, n_discrete_steps=n_discrete_steps,
                                          refinement_distance=refinement_distance,
                                          print_intermediate=print_intermediate,
                                          reachability_time_step=reachability_time_step, log=log)
    print("Result:", ha)
    assert True


if __name__ == "__main__":
    load_julia_libraries(log=True)
    reset_seed(1234)

    # test_synthesis([pwld_function_2()])
    # test_synthesis([pwld_function_3()])
    # test_simulation(hybrid_automaton_1())
    # test_simulation(hybrid_automaton_thermostat_linear())
    # test_simulation(hybrid_automaton_thermostat_affine())
    # test_imitation_thermostat(hybrid_automaton_thermostat_linear())
    # test_imitation_thermostat(hybrid_automaton_thermostat_affine())
    # test_imitation_linear_switching(hybrid_automaton_linear_switching())
    # test_imitation_two_tanks(hybrid_automaton_two_tanks_linear())
    # test_imitation_two_tanks(hybrid_automaton_two_tanks_affine())
    # test_imitation_gearbox(hybrid_automaton_gearbox())
    # test_synthesis_from_time_series(time_series_ekg())
