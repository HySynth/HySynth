from julia.api import Julia
JULIA = Julia()
# JULIA = Julia(compiled_modules=False)  # use this workaround on Debian instead
from julia import Main as jl
import numpy as np
import random
import time
from pathlib import Path

from hysynth.utils.dynamics import *
from hysynth.utils.sets import *


def load_julia_libraries(log=False):
    path = Path(__file__).parent / "load_julia_libraries.jl"
    t = time.time()
    jl.include(str(path))
    if log:
        print("finished loading Julia libraries after {:f} seconds".format(time.time() - t))


def dyn2julia(dyn):
    if isinstance(dyn, ConstDyn):
        b = np.array(dyn.b())
        return b
    elif isinstance(dyn, LinDyn):
        A = np.array(dyn.A())
        return A
    elif isinstance(dyn, AffDyn):
        A = np.array(dyn.A())
        b = np.array(dyn.b())
        return jl.AffDyn(A, b)
    raise(ValueError("unknown dynamics type {}".format(type(dyn))))


def set2julia(set):
    if not isinstance(set, SetRep):
        return set
    if isinstance(set, Interval):
        return jl.Interval(set._lo, set._hi)
    elif isinstance(set, BallInf):
        return jl.BallInf(set._center, set._radius)
    elif isinstance(set, Hyperrectangle):
        return jl.Hyperrectangle(set._center, set._radius)
    elif isinstance(set, HalfSpace):
        return jl.HalfSpace(set._a, set._b)
    elif isinstance(set, HPolyhedron):
        return jl.HPolyhedron(set._constraints)
    elif isinstance(set, VPolygon):
        return jl.VPolygon(set._vertices)
    raise(ValueError("unknown set type {}".format(type(set))))


def square(point, radius):
    P = jl.BallInf(point, radius)
    return P


def successor_set(dyn, time, P0):
    P1 = jl.successor(dyn2julia(dyn), time, P0)
    return P1


def is_similar_flow(P0, dyn, P1, time, return_set=False):
    return jl.is_similar_flow(P0, dyn2julia(dyn), P1, time, return_set=return_set)


def is_captured(pwld_function, x0, path, automaton, tube_radius, n_discrete_steps, refinement_distance, log=False):
    dyns1 = []
    times = []
    for dyn, time in pwld_function:
        dyns1.append(dyn2julia(dyn))
        times.append(time)
    dyns2 = [dyn2julia(automaton.get_flow(location)) for location in path]
    if log:
        log = True
    else:
        log = False
    answer, is_definite_answer = jl.analyze_sequence(dyns1, dyns2, times, x0, tube_radius, n_discrete_steps,
                                                     refinement_distance, log=log)
    return answer, is_definite_answer


def issubset(X, Y):
    return jl.issubset(X, Y)


def polytope_hull(X, Y):
    return jl.polytope_hull(X, Y)


def sample_from_set(X):
    return jl.sample(X)


def contains(X, point):
    return jl.contains(X, point)


def compute_reach_tube_hull(dyn, P0, time, time_step):
    return jl.compute_reach_tube_hull(dyn2julia(dyn), P0, time, time_step)


def trajectory2pwld_function(trajectory, hybrid_automaton=None):
    path, x0 = trajectory
    pwld_sequence = []
    for location, time, dyn in path:
        pwld_sequence.append((dyn, time))
    epsilon = 0.0
    return pwld_sequence, x0, epsilon


def convert_pwld_julia2python(dyn):
    # TODO convert linear and constant dynamics to LinDyn/ConstDyn
    # type PyCall.jlwrap: convert Julia's AffDyn to Python's AffDyn
    A, b = jl.flatten_dyn(dyn)
    return AffDyn(A, b)


def convert_set_julia2python(set):
    base_type = jl.basetype_string(set)
    if base_type == "Interval":
        lo, hi = jl.flatten_Interval(set)
        return Interval(lo, hi)
    if base_type == "BallInf":
        center, radius = jl.flatten_BallInf(set)
        return BallInf(center=center, radius=radius)
    elif base_type == "Hyperrectangle":
        center, radius = jl.flatten_Hyperrectangle(set)
        return Hyperrectangle(center=center, radius=radius)
    elif base_type == "HalfSpace":
        a, b = jl.flatten_HalfSpace(set)
        return HalfSpace(a=a, b=b)
    elif base_type == "HPolyhedron":
        constraints_jl = jl.flatten_HPolyhedron(set)
        constraints_py = [convert_set_julia2python(hs) for hs in constraints_jl]
        return HPolyhedron(constraints=constraints_py)
    elif base_type == "VPolygon":
        vertices_jl = jl.flatten_VPolygon(set)
        VPolygon_py = [v for v in vertices_jl]
        return VPolygon(vertices=VPolygon_py)
    else:
        raise(ValueError("unknown set type {}".format(base_type)))


def time_series2pwld_function(time_series, error, dyn_init=None, x0_init=None, log=False):
    if log:
        log = True
    else:
        log = False
    dyns_jl, x0, times, indices = jl.time_series_to_symbolic(time_series, error, dyn_init, x0_init, log=log)
    dyn_T_py = [(convert_pwld_julia2python(dyn), T) for (dyn, T) in zip(dyns_jl, times)]
    return dyn_T_py, x0, error


def reset_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    jl.reset_seed(seed)


def set_flow(ha, location_name, dyn):
    ha.set_flow(location_name, dyn, rounding=False, skip_rounding=True)


def Interval_jl(lo, hi):
    return jl.getInterval(lo, hi)


def BallInf_jl(center, radius):
    return jl.getBallInf(center, radius)


def Hyperrectangle_jl(center, radius):
    return jl.getHyperrectangle(center, radius)


def HalfSpace_jl(a, b):
    return jl.getHalfSpace(a, b)


def HPolyhedron_jl(constraints):
    return jl.getHPolyhedron(constraints)


def Universe_jl(dimension):
    return jl.getUniverse(dimension)
