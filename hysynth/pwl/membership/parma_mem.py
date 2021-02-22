import ppl


import hysynth.pwl.library as lib
import hysynth.pwl.ndim_library as nlib
from hysynth.pwl.hakimi_pwl.unroll_hakimi import unroll_hakimi, get_heuristic_path


# def membership(hakimi_path, hybrid_system, delta):
#
#     for hs_path in unroll_hakimi(hybrid_system=hybrid_system, hakimi_path=hakimi_path):
#         # We check if there exists an execution in hybrid_system following path
#         # with k-1 switches such that is delta-close to hakimi_path
#
#         if path_membership(hakimi_path=hakimi_path,
#                            hybrid_automaton_path=hs_path,
#                            hybrid_automaton=hybrid_system,
#                            delta=delta):
#             return True
#
#     return False
#
#
# def path_membership(hakimi_path, hybrid_automaton_path, hybrid_automaton, delta):
#     """ This function tests the membership for one hybrid_automaton_path vs the Hakimi path"""
#     ftube = lib.tube(hakimi_path, delta)
#     t = ppl.Variable(0)
#
#     # Tube F at time 0
#     P = ppl.NNC_Polyhedron(ftube[0])
#     P.add_constraint(t == 0)
#
#     # Invariant polyhedron of the first location in hybrid_automaton_path
#     I = hybrid_automaton.get_invariant(hybrid_automaton_path[0])  # Invariant should be a polyhedron
#
#     # Intersection of tube F at time 0 and invariant
#     P.intersection_assign(I)
#
#     if P.is_empty():
#         return False
#
#     for current_location, F1, next_location, F2 in zip(hybrid_automaton_path[:-1],
#                                                        ftube[:-1],
#                                                        hybrid_automaton_path[1:],
#                                                        ftube[1:]):
#
#         # Intersection of the two tube pieces (not empty by construction)
#         Q = ppl.NNC_Polyhedron(F1)
#         Q.intersection_assign(F2)
#
#         dynamics1 = hybrid_automaton.get_flow(current_location)["var1"]
#         dynamics2 = hybrid_automaton.get_flow(next_location)["var1"]
#
#         # guard should be a polyhedron
#         G = hybrid_automaton.get_guard((current_location,
#                                         next_location))
#
#         G1 = ppl.NNC_Polyhedron(G)
#         G1.intersection_assign(F1)
#
#         G2 = ppl.NNC_Polyhedron(G)
#         G2.intersection_assign(F2)
#
#         if G1.is_empty() and G2.is_empty():
#             return False
#
#         # Computation of the region where executions included in the delta-tube
#         # of hakimi_path can start
#         auxA = lib.post(P, G1, dynamics1)
#
#         # 			A = post(Q, auxA, -dynamics2)
#         A = lib.pre(Q, auxA, -dynamics2)
#         # A = post(Q, post(P, G1, dynamics1), -dynamics2)
#
#         # auxB = post(Q, P, -dynamics1)
#         auxB = lib.pre(Q, P, -dynamics1)
#
#         B = lib.post(auxB, G2, dynamics1)
#         #  B = post(post(Q, P, -dynamics1), G2, dynamics1)
#
#         P = ppl.NNC_Polyhedron(A)
#         P.poly_hull_assign(B)  # This is the reach set
#
#         # We believe that the convex hull will be the same as A union B,
#         # but still have not a proof, so we need to check computationally
#         # to avoid a wrong assumption.
#
#         # First, we construct the union of A and B
#         # dim = A.space_dimension()
#
#         C = ppl.NNC_Polyhedron(P)
#         C.poly_difference_assign(A)  # P\A
#         C.topological_closure_assign()
#
#         D = ppl.NNC_Polyhedron(P)
#         D.poly_difference_assign(B)  # P\B
#         D.topological_closure_assign()
#
#         if not (C.is_empty() or D.is_empty() or (C == B and D == A)):
#             # print('A union B is not the convex hull of A and B')
#             raise RuntimeError("Should not happen!")
#
#         if P.is_empty():
#             return False
#
#     # this is the last part!
#
#     dynamics = hybrid_automaton.get_flow(hybrid_automaton_path[-1])["var1"]
#
#     # Tube at final time T
#     Q = ppl.NNC_Polyhedron(ftube[-1])
#     Q.add_constraint(t == hakimi_path[-1][0])
#
#     # Invariant polyhedron of the last location in hybrid_automaton_path
#     Ilast = hybrid_automaton.get_invariant(hybrid_automaton_path[-1])
#
#     # Reachable region
#     Q.intersection_assign(Ilast)
#
#     # Reach set
#     P = lib.post(P, Q, dynamics)
#
#     if P.is_empty():
#         return False
#
#     else:
#         return True


def membership_info(pwl_path, hybrid_automaton, ftube):

    info_list = []

    heur_path, success = get_heuristic_path(pwl_path=pwl_path, hybrid_automaton=hybrid_automaton)
    if not success:
        return False, info_list

    membership_result, ftube, Aa, Bb, j = path_membership_info(pwl_path=pwl_path,
                                                               hybrid_automaton_path=heur_path,
                                                               hybrid_automaton=hybrid_automaton,
                                                               ftube=ftube)

    if membership_result:
        return True, []

    for hs_path in unroll_hakimi(hybrid_system=hybrid_automaton, hakimi_path=pwl_path):
        # We check if there exists an execution in hybrid_automaton following path
        # with k-1 switches such that is delta_fh-close to pwl_path

        membership_result, ftube, Aa, Bb, j = path_membership_info(pwl_path=pwl_path,
                                                                   hybrid_automaton_path=hs_path,
                                                                   hybrid_automaton=hybrid_automaton,
                                                                   ftube=ftube)
        if membership_result:
            return True, []
        else:
            info_list.append([ftube, Aa, Bb, hs_path, j])

    # return all the mem_info_list
    return False, info_list


def path_membership_info(pwl_path, hybrid_automaton_path, hybrid_automaton, ftube):
    """ This function tests the membership for one hybrid_automaton_path vs the PWL path"""
    t = ppl.Variable(0)

    # Initialization of list of A's and B's polyhedra
    dim = hybrid_automaton.dim + 1
    empty_polyhedron = ppl.NNC_Polyhedron(dim, 'empty')
    Aa = []
    Bb = []
    for i in range(len(pwl_path)):
        Aa.append(empty_polyhedron)
        Bb.append(empty_polyhedron)

    # Tube F at time 0
    P = ppl.NNC_Polyhedron(ftube[0])
    P.add_constraint(t == 0)

    # Invariant polyhedron of the first location in hybrid_automaton_path
    inv = hybrid_automaton.get_invariant(hybrid_automaton_path[0])  # Invariant should be a polyhedron

    # Intersection of tube F at time 0 and invariant
    P.intersection_assign(inv)

    index = 0
    Aa[index] = P
    Bb[index] = P



    if P.is_empty():
        return False, ftube, Aa, Bb, index

    # index = 0
    index += 1

    for current_location, F1, next_location, F2 in zip(hybrid_automaton_path[:-1],
                                                       ftube[:-1],
                                                       hybrid_automaton_path[1:],
                                                       ftube[1:]):

        # Intersection of the two tube pieces (not empty by construction)
        Q = ppl.NNC_Polyhedron(F1)
        Q.intersection_assign(F2)

        dynamics1 = hybrid_automaton.get_flow(current_location)
        dynamics2 = hybrid_automaton.get_flow(next_location)

        # guard should be a polyhedron
        grd = hybrid_automaton.get_guard((current_location,
                                        next_location))

        G1 = ppl.NNC_Polyhedron(grd)
        G1.intersection_assign(F1)

        G2 = ppl.NNC_Polyhedron(grd)
        G2.intersection_assign(F2)

        if G1.is_empty() and G2.is_empty():
            return False, ftube, Aa, Bb, index

        # Computation of the region where executions included in the delta-tube
        # of pwl_path can start
        auxA = nlib.npost(P, G1, dynamics1)
        if auxA.is_empty():
            A = auxA
        else:
            A = nlib.npre(Q, auxA, dynamics2)

        Aa[index] = A

        auxB = nlib.npre(Q, P, dynamics1)
        if auxB.is_empty():
            B = auxB
        else:
            B = nlib.npost(auxB, G2, dynamics1)

        Bb[index] = B

        P = ppl.NNC_Polyhedron(A)
        P.poly_hull_assign(B)  # This is the reach set

        # We believe that the convex hull will be the same as A union B.
        # Below is a computational check.

        # First, we construct the union of A and B

        # C = ppl.NNC_Polyhedron(P)
        # C.poly_difference_assign(A)  # P\A
        # C.topological_closure_assign()
        #
        # D = ppl.NNC_Polyhedron(P)
        # D.poly_difference_assign(B)  # P\B
        # D.topological_closure_assign()
        #
        # if not (C.is_empty() or D.is_empty() or (C == B and D == A)):
        #     # print('A union B is not the convex hull of A and B')
        #     raise RuntimeError("Should not happen!")happen

        if P.is_empty():
            return False, ftube, Aa, Bb, index

        index += 1

    # this is the last part!

    dynamics = hybrid_automaton.get_flow(hybrid_automaton_path[-1])

    # Tube at final time T
    Q = ppl.NNC_Polyhedron(ftube[-1])
    time_linexp = lib.integer_time_constraint(Q.space_dimension(), pwl_path[-1][0])
    # Q.add_constraint(t == pwl_path[-1][0])
    Q.add_constraint(time_linexp == 0)

    # Invariant polyhedron of the last location in hybrid_automaton_path
    Ilast = hybrid_automaton.get_invariant(hybrid_automaton_path[-1])

    # Reachable region
    Q.intersection_assign(Ilast)

    # Reach set
    P = nlib.npost(P, Q, dynamics)

    Aa[index] = P
    Bb[index] = P

    return not P.is_empty(), ftube, Aa, Bb, index


if __name__ == "__main__":
    raise RuntimeError("This module should not be directly!")

