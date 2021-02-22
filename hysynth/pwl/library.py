"""
This module contains all the commonly used functions within the software package
"""
import more_itertools
import numpy as np
from scipy.spatial import ConvexHull
from fractions import Fraction
from warnings import warn

from hysynth.utils.hybrid_system.library import construct_location_name

""" MIRIAM ----------------------------------------------------------------- START """
import ppl
from math import gcd
from functools import reduce
""" MIRIAM ----------------------------------------------------------------- END """


NDIGITS_ROUNDING = 8


def find_contiguous_blocks(iterable):
    """ This function finds blocks of consecutive numbers

    Credit: Pylang https://stackoverflow.com/questions/2154249/identify-groups-of-continuous-numbers-in-a-list
    """
    for group in filter(lambda x: len(x) >= 2, map(list, more_itertools.consecutive_groups(iterable))):
        yield group[0], group[-1]


def find_identical_blocks(iterable):

    for idx, (first, second) in enumerate(zip(iterable[0:-1], iterable[1:])):
        if first == second:
            continue
        else:
            yield idx, first, second


def contract_path(iterable):
    """ Make a path just a continuation of unique "letters" and compress all repetitions

    Example: AAABBBBBAAAAAAAACCCABC -> ABACABC

    """

    # check if iterable is empty
    if len(iterable) == 0:
        raise ValueError("Empty iterable!")

    contracted_path = list()
    for element in iterable:
        if len(contracted_path) == 0:
            contracted_path.append(element)
        else:
            if contracted_path[-1] != element:
                contracted_path.append(element)

    return contracted_path


def segment_signal(signal, segment_delimiters):
    """ Partitions a signal based on the provided change point list """

    signal_length = signal.shape[0]

    if not all(0 <= el <= signal_length - 1 for el in segment_delimiters):
        raise ValueError("Delimiters out of bounds!")

    # first delimiter must always be zero
    if 0 not in segment_delimiters:
        segment_delimiters = [0] + segment_delimiters

    # last delimiter is the last element of the signal
    if signal_length - 1 not in segment_delimiters:
        segment_delimiters.append(signal_length - 1)

    return {(point1, point2): signal[point1: point2 + 1] for point1, point2 in zip(segment_delimiters[:-1],
                                                                                   segment_delimiters[1:])}


def points_in_hull(points, convex_hull):
    """ Computes if the points are in hull and outputs a bool vector """
    return np.apply_along_axis(lambda point: point_in_hull(point, convex_hull), axis=1, arr=points)


def point_in_hull(point, convex_hull, tolerance=1e-12):
    """ Computes if a point is within a ConvexHull

    Much thanks: https://stackoverflow.com/questions/51771248/checking-if-a-point-is-in-convexhull/51786843#51786843
    """
    if not isinstance(convex_hull, ConvexHull):
        raise TypeError("Convex_hull must be a convex_hull object!")

    return all((np.dot(eq[:-1], point) + eq[-1] <= tolerance) for eq in convex_hull.equations)


def get_vertices(polyhedron):
    """ Gets the vertex points of a polyhedron as a list of tuples """

    # get the generators from the polyhedron
    curr_poly_generators = polyhedron.generators()

    list_of_vertices = list()

    # create the variables
    ppl_variables = list()
    for var_id in range(polyhedron.space_dimension()):
        ppl_variables.append(ppl.Variable(var_id))

    # loop over the generators
    for curr_gen_item in curr_poly_generators:

        # only take points
        if curr_gen_item.is_point():

            # extract value, turn into tuple add to list
            divisor = int(curr_gen_item.divisor())
            coeffs = [int(curr_gen_item.coefficient(var)) / divisor for var in ppl_variables]

            list_of_vertices.append(tuple(coeffs))

    return list_of_vertices


def get_intervals(polyhedron):
    """
    given a polyhedron that is only bounded in one dimension, return the lower and the upper bound
    :param polyhedron: polyhedron, assumed to be bounded in one dimension (i.e., an embedded interval)
    :return: a tuple (lb, up) with the lower and upper bound of the polyhedron in the bounded dimension
    """
    constraints = polyhedron.constraints()
    if len(constraints) % 2 != 0 or len(constraints) == 0:
        raise ValueError("Expected a polyhedron with an even and positive number of constraints!")
    n = int(len(constraints) / 2)
    intervals = [[None, None] for i in range(n)]
    for constraint in constraints:
        j = -1
        coefficients = constraint.coefficients()
        for i, coefficient in enumerate(coefficients):
            if coefficient == 0:
                continue
            if j != -1:
                raise ValueError("Constraints need to be over a single variable!")
            j = i
        # upper bound: 1, lower bound: 0
        k = 1 if coefficients[j] < 0 else 0
        # 'j-1' because dimension 0 is occupied by time
        intervals[j-1][k] = -(constraint.inhomogeneous_term() / coefficients[j])
    return intervals


def round_flow(flow):
    """
    round the given flow
    :param flow: vector = list of numbers
    :return: the same vector whose numbers are rounded
    """
    for i in range(len(flow)):
        flow[i] = round(flow[i], ndigits=NDIGITS_ROUNDING)
    return flow


def box_constraints_to_string(polyhedron):
    """
    pretty-print constraints for lower and upper bounds in all dimensions
    :param polyhedron: PPL polyhedron describing a box
    :return: string representation of the box
    """
    intervals = get_intervals(polyhedron)
    string = "["
    for interval in intervals:
        if string != "[":
            string += " & "
        string += "{} ≤ x ≤ {}".format(interval[0], interval[1])
    string += "]"
    return string


def check_clustering_bandwidth(bandwidth):
    if not (isinstance(bandwidth, (float, int)) or
            (isinstance(bandwidth, bool) and
             bandwidth is False)):
        raise TypeError("The argument <epsilon_meanshift> must be numeric or False!")


""" MIRIAM ----------------------------------------------------------------- START """


def post(initpoly, finalpoly, slope):
    """ Obtain a reach polyhedron given two polyhedra, the initial and the final one,
    and the dynamics as a vector of floats.
    ------------------------------------------------------------------------------------
    input:	initpoly		Initial polyhedron		ppl.NNC_Polyhedron
            finalpoly		Final polyhedron		ppl.NNC_Polyhedron
            slope			Dynamical slope			vector of floats

    output:	reachpoly		Reach polyhedron		ppl.NNC_Polyhedron.
    """
    dim = initpoly.space_dimension()

    if initpoly.is_empty() or finalpoly.is_empty():
        warn('empty initial or final set for \'post\' computation')
        return ppl.NNC_Polyhedron(dim, 'empty')

    # Minkowski sum of the initial polyhedron and the dynamics
    gen = ppl.Generator_System(initpoly.minimized_generators())

    # rays of the dynamics
    num_slopes, den_slope = float2int(slope, return_lcm=True)

    ray = ppl.Generator.ray(ppl.Linear_Expression([den_slope] + num_slopes, 0))

    # insert ray into the generators
    gen.insert(ray)
    # 	print 'generators =',gen

    # construct the polyhedron generated by the initial polyhedron and the dynamics
    reachpoly = ppl.NNC_Polyhedron(gen)
    # 	print 'reachpoly =',reachpoly.minimized_constraints()

    # Intersection of the Minkowski sum and final polyhedron,
    # which gives the reach set.
    reachpoly.intersection_assign(finalpoly)
    # 	print 'reachpoly after intersection =',reachpoly.minimized_constraints()

    return reachpoly


# ---------------------------------------------------------------------------------------#
def pre(initpoly, finalpoly, slope):
    """ Obtain a reach polyhedron given two polyhedra, the initial and the final one,
	and the slope of the dynamics.
	------------------------------------------------------------------------------------
	input:	initpoly		Initial polyhedron		ppl.NNC_Polyhedron
			finalpoly		Final polyhedron		ppl.NNC_Polyhedron
			slope			Dynamical slope			float

	output:	reachpoly		Reach polyhedron		ppl.NNC_Polyhedron. """

    dim = initpoly.space_dimension()

    if initpoly.is_empty() or finalpoly.is_empty():
        reachpoly = ppl.NNC_Polyhedron(dim,'empty')

    else:
        # Get the generators from the initial polyhedron
        initgen = initpoly.minimized_generators()

        # Minkowski sum of the initial polyhedron and the dynamics
        gen = ppl.Generator_System()

        # generators of the initial polyhedron
        for g in initgen:
            gen.insert(g)

        # rays of the dynamics
        rat_slope = Fraction(str(slope))
        den_slope = rat_slope.denominator
        num_slope = rat_slope.numerator

        d = ppl.Generator.ray(-den_slope * ppl.Variable(0) + num_slope * ppl.Variable(1))

        # insert ray into the generators
        gen.insert(d)
        # 	print 'generators =',gen

        # construct the polyhedron generated by the initial polyhedron and the dynamics
        reachpoly = ppl.NNC_Polyhedron(gen)
        # 	print 'reachpoly =',reachpoly.minimized_constraints()

        # Intersection of the Minkowski sum and final polyhedron,
        # which gives the reach set.
        reachpoly.intersection_assign(finalpoly)

    return reachpoly


# ---------------------------------------------------------------------------------------#
def lcm(numbers):
    """ Get the least common multiple of a list of numbers
	------------------------------------------------------------------------------------
		input: 	numbers		[1,2,6]		list of integers
		output:				6			integer """
    return reduce(lambda x, y: int((x * y) / gcd(x, y)), numbers, 1)


# ---------------------------------------------------------------------------------------#
def float2int(floatlist, return_lcm=False):
    """ Obtain a integer list from a list of floats by multiplying every float by the
	same value.
	------------------------------------------------------------------------------------
	input:	floatlist		list of float

	output:	intlist			list of integer."""

    from fractions import Fraction

    # 	print 'float list =', floatlist
    rationallist = []
    denominatorlist = []
    for flt in floatlist:
        rational = Fraction(str(flt))
        rationallist.append(rational)
        denominatorlist.append(int(rational.denominator))

    # Least common multiple of the denominators
    LCM = lcm(denominatorlist)

    #	For optimising we should check if LCM = 1, and in that case just do the following
    if LCM == 1:
        integerlist = [int(rational) for rational in rationallist]

    integerlist = []
    for rational in rationallist:
        integer = int(rational.numerator * LCM / rational.denominator)
        integerlist.append(integer)

    # print('integer list =',integerlist)
    if return_lcm:
        return integerlist, LCM
    return integerlist


# ---------------------------------------------------------------------------------------#
def slopes(f):
    """ Obtain the slopes of each affine piece of the PWL function f.
	------------------------------------------------------------------------------------
	input:  f		        PWL function points		list of lists

	output:	slopes			values of the slopes	list of float vectors. """

    function_slope = []

    # 	for piece in f:

    if len(f) > 0:
        n = len(f[0])
    for i in range(len(f) - 1):
        f_i = f[i]
        f_ip1 = f[i+1]

        delta_t = f_ip1[0] - f_i[0]  # time distance

        # Compute coefficients of the piece of f : at + bx + c = 0
        # Then, bx = -at -c, which is x = -a/b t - c/b
        piece_slope = []
        for j in range(1, n):
            slope = (f_ip1[j] - f_i[j]) / delta_t
            slope = round_flow([slope])[0]
            piece_slope.append(slope)

        function_slope.append(piece_slope)

    return function_slope


# ---------------------------------------------------------------------------------------#
def projection(poly, coordlist):
    """ Obtains the projected polyhedron in a subspace of the total space.
		input:  poly            ppl.NNC_Polyhedron
				coordlist		integer list
		output: projpoly        ppl.NNC_Polyhedron. """

    dim = poly.space_dimension()

    if poly.is_empty():
        return ppl.NNC_Polyhedron(dim, 'empty')

    elif poly.is_universe():
        return ppl.NNC_Polyhedron(dim, 'universe')

    else:

        projpoly = ppl.NNC_Polyhedron(poly)
        polycoord = ppl.NNC_Polyhedron(dim, 'universe')

        for i in range(dim):
            if i not in coordlist:
                projpoly.unconstrain(ppl.Variable(i))
            # polycoord.add_constraint(Variable(i)==0)

        projpoly.intersection_assign(polycoord)

    return projpoly


# ---------------------------------------------------------------------------------------#
def reach_AB(A, B, init_dynamics, final_dynamics, initF, finalF, G):
    dim = G.space_dimension()

    P = ppl.NNC_Polyhedron(A)
    P.poly_hull_assign(B)

    # Intersection of the two tube pieces (not empty by construction)
    Q = ppl.NNC_Polyhedron(initF)
    Q.intersection_assign(finalF)

    if G.is_universe():
        G1 = ppl.NNC_Polyhedron(initF)
        G2 = ppl.NNC_Polyhedron(finalF)
    else:
        G1 = ppl.NNC_Polyhedron(G)
        G1.intersection_assign(initF)

        G2 = ppl.NNC_Polyhedron(G)
        G2.intersection_assign(finalF)

    if G1.is_empty():
        reachA = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        # Computation of the region where executions included in the delta-tube
        # of f can start
        auxA = post(P, G1, init_dynamics)
        reachA = pre(Q, auxA, -final_dynamics)

    if G2.is_empty():
        reachB = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        auxB = pre(Q, P, -init_dynamics)
        reachB = post(auxB, G2, init_dynamics)

    return reachA, reachB


# ---------------------------------------------------------------------------------------#
def reach_A(A, B, init_dynamics, final_dynamics, initF, finalF, G):
    dim = G.space_dimension()

    P = ppl.NNC_Polyhedron(A)
    P.poly_hull_assign(B)

    # Intersection of the two tube pieces (not empty by construction)
    Q = ppl.NNC_Polyhedron(initF)
    Q.intersection_assign(finalF)

    if G.is_universe():
        G1 = ppl.NNC_Polyhedron(initF)
    else:
        G1 = ppl.NNC_Polyhedron(G)
        G1.intersection_assign(initF)

    if G1.is_empty():
        reachA = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        # Computation of the region where executions included in the delta-tube
        # of f can start
        auxA = post(P, G1, init_dynamics)
        reachA = pre(Q, auxA, -final_dynamics)

    return reachA


# ---------------------------------------------------------------------------------------#
def reach_last_A(A, B, dynamics, F, final_time, Inv):
    dim = A.space_dimension()

    P = ppl.NNC_Polyhedron(A)
    P.poly_hull_assign(B)

    # Intersection of the two tube pieces (not empty by construction)
    Q = ppl.NNC_Polyhedron(F)
    # Q.add_constraint(ppl.Variable(0) == final_time)
    time_linexp = integer_time_constraint(Q.space_dimension(), final_time)
    Q.add_constraint(time_linexp == 0)

    if not Inv.is_universe():
        Q.intersection_assign(Inv)

    if Q.is_empty():
        reachA = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        reachA = post(P, Q, dynamics)

    return reachA


# ---------------------------------------------------------------------------------------#
def reach_B(A, B, init_dynamics, initF, finalF, G):
    dim = G.space_dimension()

    P = ppl.NNC_Polyhedron(A)
    P.poly_hull_assign(B)

    # Intersection of the two tube pieces (not empty by construction)
    Q = ppl.NNC_Polyhedron(initF)
    Q.intersection_assign(finalF)

    if G.is_universe():
        G2 = ppl.NNC_Polyhedron(finalF)
    else:
        G2 = ppl.NNC_Polyhedron(G)
        G2.intersection_assign(finalF)

    if G2.is_empty():
        reachB = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        auxB = pre(Q, P, -init_dynamics)
        reachB = post(auxB, G2, init_dynamics)

    return reachB


# ---------------------------------------------------------------------------------------#
def reach_P(P, init_dynamics, final_dynamics, initF, finalF, G):
    dim = P.space_dimension()

    # Intersection of the two tube pieces (not empty by construction)
    Q = ppl.NNC_Polyhedron(initF)
    Q.intersection_assign(finalF)

    if G.is_universe():
        G1 = ppl.NNC_Polyhedron(initF)
        G2 = ppl.NNC_Polyhedron(finalF)
    else:
        G1 = ppl.NNC_Polyhedron(G)
        G1.intersection_assign(initF)

        G2 = ppl.NNC_Polyhedron(G)
        G2.intersection_assign(finalF)

    if G1.is_empty():
        A = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        # Computation of the region where executions included in the delta-tube
        # of f can start
        auxA = post(P, G1, init_dynamics)
        A = pre(Q, auxA, -final_dynamics)

    if G2.is_empty():
        B = ppl.NNC_Polyhedron(dim, 'empty')
    else:
        auxB = pre(Q, P, -init_dynamics)
        B = post(auxB, G2, init_dynamics)

    reachP = ppl.NNC_Polyhedron(A)
    reachP.poly_hull_assign(B)

    return reachP


# ---------------------------------------------------------------------------------------#
def integer_time_constraint(dim,time_value):
    """ Construct the left side of a constraint of the form t - a ~ 0, where ~ in {<=,>=,=},
    t is the time variable and a is the time_value.
    ------------------------------------------------------------------------------------
    input:	dim                 integer
            time_value          float

    output:	time_linexp         ppl.Linear_Expression. """

    time_coefficients = [0] * dim
    time_coefficients[0] = 1
    time_coefficients.append(-time_value)

    if time_value.is_integer():
        time_linexp = ppl.Linear_Expression(
            [time_coefficients[i] for i in range(len(time_coefficients) - 1)],
            time_coefficients[-1])
    else:
        time_integer_coefficients = float2int(time_coefficients)
        time_linexp = ppl.Linear_Expression([time_integer_coefficients[i] for i in range(len(time_integer_coefficients) - 1)], time_integer_coefficients[-1])

    return time_linexp


# ---------------------------------------------------------------------------------------#
def tube(f, delta):
    F = []
    function_slopes = slopes(f)
    n = len(f[0])

    # 	for piece in f:

    for i in range(len(f) - 1):
        f_i = f[i]
        init_t = f_i[0]  # Initial time instant
        final_t = f[i + 1][0]  # Final time instant

        # i-th tube piece
        G = ppl.NNC_Polyhedron(n, 'universe')

        # add time constraints
        lower_time_le = integer_time_constraint(n, init_t)
        upper_time_le = integer_time_constraint(n, final_t)
        G.add_constraint(lower_time_le >= 0)
        G.add_constraint(upper_time_le <= 0)

        # Compute coefficients of the piece of f : at + bx + c = 0
        a = function_slopes[i]
        for j in range(1, n):
            a_j = a[j - 1]
            b_j = -1.
            c_j = f_i[j] - a_j * init_t

            upper_coefficients = [a_j, b_j, c_j + delta]
            lower_coefficients = [a_j, b_j, c_j - delta]

            uic = float2int(upper_coefficients)
            lic = float2int(lower_coefficients)
            upper_lhs = [uic[0]] + ([0] * (j-1)) + [uic[1]] + ([0] * (n-j-1))
            lower_lhs = [lic[0]] + ([0] * (j-1)) + [lic[1]] + ([0] * (n-j-1))
            upper_rhs = uic[2]
            lower_rhs = lic[2]

            G.add_constraint(ppl.Linear_Expression(upper_lhs, upper_rhs) >= 0)
            G.add_constraint(ppl.Linear_Expression(lower_lhs, lower_rhs) <= 0)

        F.append(G)

    return F


# ---------------------------------------------------------------------------------------#
def convex_hull(polyhedron1, polyhedron2):

    ch_polyhedron = ppl.NNC_Polyhedron(polyhedron1)
    ch_polyhedron.poly_hull_assign(polyhedron2)

    return ch_polyhedron


# ---------------------------------------------------------------------------------------#
def intersection(polyhedron1, polyhedron2):

    polyhedron = ppl.NNC_Polyhedron(polyhedron1)
    polyhedron.intersection_assign(polyhedron2)

    return polyhedron


# ---------------------------------------------------------------------------------------#
def equal_vectors(vector1, vector2):

    if vector1 is None and vector2 is None:
        return True
    elif vector1 is None or vector2 is None:
        return False
    else:
        for i in range(len(vector1)):

            if vector1[i] != vector2[i]:
                return False

    return True


""" MIRIAM ----------------------------------------------------------------- END """


def merge(ha1, ha2):
    """
    Merge the second hybrid automaton into the first one. By "merging" we mean to merge
    two locations iff they have the same slope; transitions are merged in the obvious
    way, and constraints become the convex hull.
    :param ha1: first hybrid automaton, to be modified
    :param ha2: second hybrid automaton, unmodified
    :return: the modified first automaton
    """
    slope_to_loc1 = dict()
    for loc1 in ha1.locations:
        slope_to_loc1[tuple(ha1.get_flow(loc1))] = loc1

    # find and merge locations
    loc2_to_loc1 = dict()
    k = len(ha1.locations)
    for loc2 in ha2.locations:
        slope = tuple(ha2.get_flow(loc2))
        loc1 = slope_to_loc1.get(slope)
        if loc1 is None:
            # no corresponding location, create a new one and set the flow and invariant
            loc1 = construct_location_name(k)
            ha1.add_location(loc1)
            ha1.set_flow(loc1, list(slope))
            invariant = ha2.get_invariant(loc2)
            slope_to_loc1[slope] = loc1
            k += 1
        else:
            # update invariant
            inv1 = ha1.get_invariant(loc1)
            inv2 = ha2.get_invariant(loc2)
            invariant = convex_hull(inv1, inv2)
        ha1.set_invariant(loc1, invariant)
        loc2_to_loc1[loc2] = loc1

    # add transitions
    transitions1 = ha1.edges
    for transition2 in ha2.edges:
        grd2 = ha2.get_guard(transition2)
        transition2_mapped = (loc2_to_loc1[transition2[0]], loc2_to_loc1[transition2[1]])
        if transition2_mapped in transitions1:
            # update guard
            grd1 = ha1.get_guard(transition2_mapped)
            guard = convex_hull(grd1, grd2)
        else:
            # no corresponding transition => add it
            ha1.add_edge(transition2_mapped[0], transition2_mapped[1])
            guard = grd2
        ha1.set_guard(transition2_mapped, guard)

    return ha1


if __name__ == "__main__":
    raise RuntimeError("This is a library module, it should not be run directly!")  # pragma: no cover
