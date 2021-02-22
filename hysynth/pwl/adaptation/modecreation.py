# standard library imports
import random

# external packages
import numpy as np
import ppl

import hysynth.pwl.library as lib
import hysynth.pwl.ndim_library as nlib
from hysynth.pwl.hakimi_pwl.unroll_hakimi import get_heuristic_path


def mode_addition(H, name, inv, flow, in_edge = None, in_guard = None, out_edge = None, out_guard = None):

    """ Add a mode to a hybrid automaton
	------------------------------------------------------------------------------------
	input:	H				Hybrid automaton			HybridSystemABC
			name			Name of the location		string
			inv				Invariant					ppl.NNC_Polyhedron
			flow			Dynamics					float
			in_edge			Incoming edge				tuple of floats
			in_guard		Incoming guard				ppl.constraint
			out_edge		Outgoing edge				tuple of floats
			out_guard		Outgoing guard				ppl.constraint
			
	output:	H				Hybrid automaton			HybridSystemABC. """


    H.add_location(name)
    H.set_invariant(name, inv)
    H.set_flow(name, flow)

    if in_edge:
        H.add_edge(*in_edge)
        H.set_guard(in_edge, in_guard)

    if out_edge:
        H.add_edge(*out_edge)
        H.set_guard(out_edge, out_guard)

    return H


def create_mode(new_H, P, initF, finalF, slope, pre_location, location, post_location):

    dim = P.space_dimension()

    auxInv = lib.post(P, initF, slope)

    Inv = lib.projection(auxInv, [1])
    flow = slope

    if pre_location:
        in_edge = (pre_location, location)
        in_guard = lib.projection(P, [1])

    else:
        in_edge = []
        in_guard = ppl.NNC_Polyhedron(dim, 'empty')

    if post_location:
        out_edge = (location, post_location)

        G = ppl.NNC_Polyhedron(dim, 'universe')
        reachP = lib.reach_P(P, slope, new_H.get_flow(post_location)["var1"], initF, finalF, G)

        out_guard = lib.projection(reachP, [1])

    else:

        out_edge = []
        out_guard = ppl.NNC_Polyhedron(dim, 'empty')

    # skip duplicates
    if any([np.isclose(flow, ex_flow["var1"]) for ex_flow in new_H.flows.values()]):
        raise ValueError("You just tried to duplicate a mode!")

    new_H = mode_addition(new_H, location, Inv, {'var1': flow}, in_edge, in_guard, out_edge, out_guard)

    return new_H


def slope_bound(init_point, final_point, delta):
    """ Obtain a flow in the hybrid automaton H which is close to the slope form by
    joining two points: initial and final. """

    init_t = init_point[0]  # Initial time instant
    final_t = final_point[0]  # Final time instant

    init_x = init_point[1]  # Initial value
    final_x = final_point[1]  # Final value

    # Exact slope
    slope = (final_x - init_x) / (final_t - init_t)  # this is the slope value

    # Upper bound for the slope value
    final_x_up = final_x + delta
    slope_upper = (final_x_up - init_x) / (final_t - init_t)

    # Lower bound for the slope value
    final_x_low = final_x - delta
    slope_lower = (final_x_low - init_x) / (final_t - init_t)

    return slope, slope_lower, slope_upper


def similar_flow_mode(init_point, final_point, hybrid_automaton):
    """ Obtain a flow in the hybrid automaton H which is close to the slope form by
    joining two points: initial and final. """

    slope, slope_lower, slope_upper = slope_bound(init_point, final_point, hybrid_automaton.delta)

    min_diff_slope = float('inf')
    resulting_mode = None

    for curr_mode_name, flow in hybrid_automaton.flows.items():
        # current flow
        flow = flow["var1"]

        if slope_lower <= flow <= slope_upper and flow - slope < min_diff_slope:
            min_diff_slope = flow - slope
            resulting_mode = curr_mode_name

    return resulting_mode


def longest_matching_path(pwl_f_list, hybrid_automaton):
    """ Function returns the path with the closest matching modes, None means no match found """
    return [similar_flow_mode(init_point, final_point, hybrid_automaton)
            for init_point, final_point in pwl_f_list]


def mode_modification(H, mode_name, inv, in_edge, in_guard, out_edge, out_guard):
    """ Add a mode to a hybrid automaton
	------------------------------------------------------------------------------------
	input:	H				Hybrid automaton			HybridSystemABC
			name			Name of the location		string
			inv				Invariant					ppl.NNC_Polyhedron
			flow			Dynamics					float
			in_edge			Incoming edge				tuple of floats
			in_guard		Incoming guard				ppl.constraint
			out_edge		Outgoing edge				tuple of floats
			out_guard		Outgoing guard				ppl.constraint

	output:	H				Hybrid automaton			HybridSystemABC. """

    auxInv = H.get_invariant(mode_name)
    newInv = lib.convex_hull(auxInv,inv)
    H.set_invariant(mode_name,newInv) # Is this the correct way for modifying the invariant?

    # If in_edge exists (It could be the case that is an empty list)
    if in_edge:
        if in_edge in H.edges:

            auxG = H.get_guard(in_edge)
            newG = lib.convex_hull(auxG, in_guard)

            H.remove_guard(in_edge)
            H.set_guard(in_edge,newG)

        else:

            H.add_edge(*in_edge)
            H.set_guard(in_edge,in_guard)

    # If out_edge exists (It could be the case that is an empty list)
    if out_edge:
        if out_edge in H.edges:

            auxG = H.get_guard(out_edge)
            newG = lib.convex_hull(auxG,out_guard)

            H.remove_guard(out_edge)
            H.set_guard(out_edge,newG)

        else:

            H.add_edge(*out_edge)
            H.set_guard(out_edge,out_guard)

    return H


def modify_mode(H, P, initF, finalF, pre_location, location, post_location):

    dim = P.space_dimension()

    slope = H.get_flow(location)['var1']
    auxInv = lib.post(P, initF, slope)

    Inv = lib.projection(auxInv, [1])

    if pre_location:

        in_edge = (pre_location, location)
        in_guard = lib.projection(P, [1])

    else:

        in_edge = []
        in_guard = ppl.NNC_Polyhedron(dim,'empty')

    if post_location:

        out_edge = (location, post_location)

        G = ppl.NNC_Polyhedron(dim, 'universe')
        reachP = lib.reach_P(P, slope, H.get_flow(post_location)['var1'], initF, finalF, G)
        out_guard = lib.projection(reachP, [1])

    else:

        out_edge = []
        out_guard = ppl.NNC_Polyhedron(dim,'empty')

    H = mode_modification(H, location, Inv, in_edge, in_guard, out_edge, out_guard)

    return H


def modify_ha(old_ha, mod_ha, path):
    """
    Construct a new hybrid automaton that contains only those new locations and transitions in the modified automaton
    that are necessary along the given path.

    :param old_ha: old hybrid automaton
    :param mod_ha: modified hybrid automaton
    :param path: path in the modified hybrid automaton
    :return: new hybrid automaton (a modification of 'old_ha')
    """
    new_ha = old_ha.copy()

    for loc in path:

        if loc != None:

            inv = mod_ha.get_invariant(loc)

            if loc not in new_ha.locations:
                # add location
                new_ha.add_location(loc)
                new_ha.set_flow(loc, mod_ha.get_flow(loc), rounding=True)

            # set/overwrite the invariant
            new_ha.set_invariant(loc, inv)

    for loc1, loc2 in zip(path[:-1], path[1:]):

        if loc1 != None and loc2 != None:

            trans = (loc1, loc2)
            grd = mod_ha.get_guard(trans)

            if trans not in new_ha.edges:
                # add transition
                new_ha.add_edge(loc1, loc2)

            # set/overwrite the guard
            new_ha.set_guard(trans, grd)

    return new_ha


def create_name(proposed, hybrid_automaton):
    new_name = proposed

    while new_name in hybrid_automaton.locations:
        new_name = "{}_{}".format(proposed, str(random.randint(0, 1000)))

    return new_name


def wrapper_adapt_ha(current_pwl_f, hybrid_automaton, data_index, mem_info, ftube):
    """ This is just a wrapper until the code gets reorganized and cleaned up """

    # region: here is the monkeypatch inserting the heuristic

    # first we get the heuristic path based on guided search
    heur_path, _ = get_heuristic_path(pwl_path=current_pwl_f, hybrid_automaton=hybrid_automaton)

    # find the path in mem_info
    mem_info_entry = None
    for m_info_entry in mem_info:
        if m_info_entry[3] == heur_path:
            mem_info_entry = m_info_entry
            break

    dim = hybrid_automaton.dim + 1
    empty_polyhedron = ppl.NNC_Polyhedron(dim, 'empty')
    if mem_info_entry is None:
        A_list = [empty_polyhedron for i in range(len(current_pwl_f) + 1)]
        B_list = [empty_polyhedron for i in range(len(current_pwl_f) + 1)]
        ha_path = heur_path
        # for i in range(len(heur_path), len(current_pwl_f)):
        #     ha_path.append(None)
        empty_index = 0
    else:
        _, A_list, B_list, ha_path, empty_index = mem_info_entry
        # for i in range(len(A_list), len(current_pwl_f) + 1):
        for i in range(len(A_list), len(current_pwl_f)):
            A_list.append(empty_polyhedron)
            B_list.append(empty_polyhedron)

    return adaptation_ha(pwl_function=current_pwl_f,
                         pwl_f_tube=ftube,
                         A_list=A_list,
                         B_list=B_list,
                         hybrid_automaton=hybrid_automaton,
                         ha_path=ha_path,
                         empty_index=empty_index,
                         data_index=data_index)




def modecreation_main(f, ftube, Aa, Bb, H, Hpath, j, k):
    """ Obtain a hybrid automaton such that it captures the behaviour of the
	PWL function f.
	------------------------------------------------------------------------------------
	input:	f				List of points: PWL function	list of list
			ftube			List of polyhedra				list of ppl.NNC_Polyhedron
			Aa				List of j polyhedra				list of ppl.NNC_Polyhedron
			Bb				List of j polyhedra				list of ppl.NNC_Polyhedron
			H				Hybrid automaton				HybridSystemABC
			Hpath			List of locations				list of HybridSystemABC.locations
			j				Index for emptiness				integer
			k				k-th time series				integer

	output:	new_H			Hybrid automaton		HybridSystemABC. """


    dim = len(f[0])

    # Copy the hybrid automaton into a new one for modifying it
    new_H = H.copy()

    # Copy the Hpath
    new_Hpath = Hpath[:]

    # Compute slopes of the PWL function f
    M = lib.slopes(f)

    # Compute the last index for the path of the hybrid automaton
    maxind = len(new_Hpath) - 1

    # We start checking the reachable sets from the index where emptiness is provided
    # In the case of getting index -1, which means that P[0] is empty, we need to evaluate
    # which is the cause
    if j == -1:
        init_mode_name = new_Hpath[0]
        I = new_H.get_invariant(init_mode_name)
        initA = ppl.NNC_Polyhedron(ftube[0])
        initA.add_constraint(ppl.Variable(0) == f[0][0])

        initP = ppl.NNC_Polyhedron(I)
        initP.intersection_assign(initA)

        if initP.is_empty():
            auxI = ppl.NNC_Polyhedron(I)
            auxI.poly_hull_assign(initA)
            newI = lib.projection(auxI, [1])
            new_H.set_invariant(init_mode_name,newI)

        i = 0

    else:
        i = j

    # While the end of the path is not reached
    while i <= maxind:

        # COMPUTE P[i] by considering the dynamics in the path from the hybrid automaton H, new_Hpath[i] and new_Hpath[i+1],
        # evolving inside the pieces ftube[i] and ftube[i+1] (this will be different for the case of i = maxind)

        # Corresponding location in the path at the i-th position
        loc1 = new_Hpath[i]

        # We access Aa[i-1] and Bb[i-1] if possible (i > 0) or we construct the previous A and B sets
        if i == 0:
            aux_A = ppl.NNC_Polyhedron(ftube[0])
            aux_A.add_constraint(ppl.Variable(0) == f[0][0])
            aux_B = ppl.NNC_Polyhedron(dim, 'empty')

        else:
            aux_A = Aa[i - 1]
            aux_B = Bb[i - 1]

        # In the case of i = maxind, there will be no i+1
        if i == maxind:

            loc2 = ''   # empty string: used later for the case of modifying or creating a mode

            I = new_H.get_invariant(loc1)
            A = lib.reach_last_A(aux_A, aux_B, new_H.get_flow(loc1)['var1'], ftube[i], f[-1][0], I)
            B = ppl.NNC_Polyhedron(dim, 'empty')

        else:

            loc2 = new_Hpath[i + 1]

            G = new_H.get_guard((loc1, loc2))

            A, B = lib.reach_AB(aux_A, aux_B, new_H.get_flow(loc1)['var1'], new_H.get_flow(loc2)['var1'], ftube[i], ftube[i + 1], G)


        P = ppl.NNC_Polyhedron(A)
        P.poly_hull_assign(B)  # We are not using A and B only here, this is why we do
        # not call reach_P directly

        if P.is_empty():

            G = ppl.NNC_Polyhedron(dim, 'universe')

            # COMPUTE P[i] by considering a different dynamics in (i+1)-th position.
            # Modify the dynamics for the i+1 position by the dynamics in the PWL function or a similar
            # dynamics in the hybrid automaton new_H, if possible (if i < maxind).
            # dynamics2 = M[i+1] or similar_flow(f[i+1],f[i+2])

            if i < maxind:

                # We compute the reach set by considering an already existing flow in the hybrid automaton
                # with a similar value to M[i+1] (determined by f[i+1] and f[i+2])
                similar_mode = similar_flow_mode(f[i+1], f[i+2], new_H)

                if similar_mode != loc2 and similar_mode is not None:

                    A, B = lib.reach_AB(aux_A, aux_B, new_H.get_flow(loc1)['var1'], new_H.get_flow(similar_mode)['var1'], ftube[i], ftube[i + 1], G)
                    mode_action = 'modification'

                    if A.is_empty() and B.is_empty():

                        A, B = lib.reach_AB(aux_A, aux_B, new_H.get_flow(loc1)['var1'], M[i + 1], ftube[i], ftube[i + 1], G)
                        mode_action = 'creation'

                else:

                    A, B = lib.reach_AB(aux_A, aux_B, new_H.get_flow(loc1)['var1'], M[i + 1], ftube[i], ftube[i + 1], G)
                    mode_action = 'creation'

                P = ppl.NNC_Polyhedron(A)
                P.poly_hull_assign(B)


            if P.is_empty():

                # COMPUTE P[i] by considering the same dynamics in i-th position and
                # modifying invariant or guard to universe polyhedron, so we do not
                # compute a similar_mode, but we assign it the i-th location in the path
                # for later modification.
                #similar_mode = loc1

                if i == 0:
                    loc0 = ''

                    aux_A = ppl.NNC_Polyhedron(ftube[0])
                    aux_A.add_constraint(ppl.Variable(0) == f[0][0])
                    aux_B = ppl.NNC_Polyhedron(dim, 'empty')

                else:

                    loc0 = new_Hpath[i-1]

                    aux_A = Aa[i - 1]
                    aux_B = Bb[i - 1]

                if i == maxind:

                    loc0 = new_Hpath[i - 1]
                    loc2 = ''  # empty string: used later for the case of modifying or creating a mode

                    I = ppl.NNC_Polyhedron(dim,'universe')
                    A = lib.reach_last_A(aux_A, aux_B, new_H.get_flow(loc1)['var1'], ftube[i], f[-1][0], I)
                    B = ppl.NNC_Polyhedron(dim, 'empty')
                    mode_action = 'modification'

                else:

                    loc2 = new_Hpath[i + 1]

                    G = ppl.NNC_Polyhedron(dim,'universe')
                    A, B = lib.reach_AB(aux_A, aux_B, new_H.get_flow(loc1)['var1'], new_H.get_flow(loc2)['var1'],
                                        ftube[i], ftube[i + 1], G)
                    mode_action = 'modification'

                P = ppl.NNC_Polyhedron(A)
                P.poly_hull_assign(B)

                if P.is_empty():
                    # COMPUTE P[i] by considering a different dynamics in i-th position.
                    # Modify the dynamics for the i position by the dynamics in the PWL function or a similar
                    # dynamics in the hybrid automaton new_H, which is always possible.
                    # dynamics1 = M[i] or similar_flow(f[i],f[i+1])

                    similar_mode = similar_flow_mode(f[i], f[i + 1], new_H)

                    # RECOMPUTE Aa[i-1] (aux_A), which requires to get Aa[i-2] (Aminus1) and Bb[i-2] in case of i > 0.
                    # This computation will be different depending on the values of i
                    if i == 0:

                        # Corresponding location in the path at the (i-1)-th position
                        loc0 = ''

                        aux_A_cre = ppl.NNC_Polyhedron(ftube[0])
                        aux_A_cre.add_constraint(ppl.Variable(0) == f[0][0])
                        aux_B_cre = ppl.NNC_Polyhedron(dim, 'empty')

                        if similar_mode != loc1 and similar_mode is not None:
                            aux_A_mod = ppl.NNC_Polyhedron(ftube[0])
                            aux_A_mod.add_constraint(ppl.Variable(0) == f[0][0])
                            aux_B_mod = ppl.NNC_Polyhedron(dim, 'empty')


                    elif i == 1:

                        # Corresponding location in the path at the (i-1)-th position
                        loc0 = new_Hpath[i - 1]

                        Aminus1 = ppl.NNC_Polyhedron(ftube[0])
                        Aminus1.add_constraint(ppl.Variable(0) == f[0][0])
                        Bminus1 = ppl.NNC_Polyhedron(dim, 'empty')

                        G = ppl.NNC_Polyhedron(dim, 'universe')

                        if similar_mode != loc1 and similar_mode is not None:
                            aux_A_mod, aux_B_mod = lib.reach_AB(Aminus1, Bminus1, new_H.get_flow(loc0)['var1'], new_H.get_flow(similar_mode)['var1'], ftube[i-1], ftube[i],G)

                        aux_A_cre, aux_B_cre = lib.reach_AB(Aminus1, Bminus1, new_H.get_flow(loc0)['var1'], M[i], ftube[i - 1], ftube[i], G)

                    else:

                        # Corresponding location in the path at the (i-1)-th position
                        loc0 = new_Hpath[i - 1]

                        G = ppl.NNC_Polyhedron(dim, 'universe')
                        Aminus1 = Aa[i-1]
                        Bminus1 = Bb[i-1]

                        if similar_mode != loc1 and similar_mode is not None:
                            aux_A_mod, aux_B_mod = lib.reach_AB(Aminus1, Bminus1, new_H.get_flow(loc0)['var1'],
                                            new_H.get_flow(similar_mode)['var1'], ftube[i - 1], ftube[i],G)

                        aux_A_cre, aux_B_cre = lib.reach_AB(Aminus1, Bminus1, new_H.get_flow(loc0)['var1'], M[i], ftube[i - 1], ftube[i], G)


                    # Next, once we have Aa[i-1] and Bb[i-1], COMPUTE the new Aa[i] (A) and Bb[i] (B)

                    if similar_mode != loc1 and similar_mode is not None:

                        if i == maxind:

                            I = ppl.NNC_Polyhedron(dim, 'universe')
                            A = lib.reach_last_A(aux_A_mod, aux_B_mod, new_H.get_flow(similar_mode)['var1'], ftube[i], f[-1][0], I)
                            B = ppl.NNC_Polyhedron(dim, 'empty')
                            mode_action = 'modification'

                        else:

                            G = ppl.NNC_Polyhedron(dim, 'universe')
                            A, B = lib.reach_AB(aux_A_mod, aux_B_mod, new_H.get_flow(similar_mode)['var1'], new_H.get_flow(loc2)['var1'], ftube[i], ftube[i+1], G)
                            mode_action = 'modification'

                            if A.is_empty() and B.is_empty():
                                A, B = lib.reach_AB(aux_A_cre, aux_B_cre, M[i], new_H.get_flow(loc2)['var1'], ftube[i], ftube[i+1], G)
                                mode_action = 'creation'

                    else:

                        if i == maxind:

                            I = ppl.NNC_Polyhedron(dim, 'universe')
                            A = lib.reach_last_A(aux_A_cre, aux_B_cre, M[i], ftube[i], f[-1][0], I)
                            B = ppl.NNC_Polyhedron(dim, 'empty')
                            mode_action = 'creation'

                        else:

                            G = ppl.NNC_Polyhedron(dim, 'universe')
                            A, B = lib.reach_AB(aux_A_cre, aux_B_cre, M[i], new_H.get_flow(loc2)['var1'], ftube[i], ftube[i+1], G)
                            mode_action = 'creation'

                    P = ppl.NNC_Polyhedron(A)
                    P.poly_hull_assign(B)

                    if P.is_empty():
                        # COMPUTE P[i-1] by considering a different dynamics in (i-1)-th position.
                        # Modify the dynamics for the i-1 position by the dynamics in the PWL function
                        # or a similar dynamics in the hybrid automaton new_H, if possible (i > 0).
                        # dynamics0 = M[i-1] or similar_flow(f[i-1],f[i])

                        similar_mode = similar_flow_mode(f[i - 1], f[i], new_H)

                        # RECOMPUTE Aa[i-2] (Aminus1), which requires to get Aa[i-3] (Aminus2) and Bb[i-3] in case of i > 1.
                        # This computation will be different depending on the values of i
                        if i == 0:
                            raise RuntimeError("Modification should have been done in a previous step!")

                        elif i == 1:
                            # Corresponding location in the path at the (i-1)-th position
                            loc0 = new_Hpath[i - 1]
                            locminus1 = ''

                            Aminus1_cre = ppl.NNC_Polyhedron(ftube[0])
                            Aminus1_cre.add_constraint(ppl.Variable(0) == f[0][0])
                            Bminus1_cre = ppl.NNC_Polyhedron(dim, 'empty')

                            if similar_mode != loc0 and similar_mode is not None:
                                Aminus1_mod = ppl.NNC_Polyhedron(ftube[0])
                                Aminus1_mod.add_constraint(ppl.Variable(0) == f[0][0])
                                Bminus1_mod = ppl.NNC_Polyhedron(dim, 'empty')

                        elif i == 2:
                            # Corresponding location in the path at the (i-1)-th position
                            loc0 = new_Hpath[i - 1]
                            locminus1 = new_Hpath[i - 2]

                            G = ppl.NNC_Polyhedron(dim, 'universe')

                            Aminus2 = ppl.NNC_Polyhedron(ftube[0])
                            Aminus2.add_constraint(ppl.Variable(0) == f[0][0])
                            Bminus2 = ppl.NNC_Polyhedron(dim, 'empty')

                            if similar_mode != loc0 and similar_mode is not None:
                                 Aminus1_mod, Bminus1_mod = lib.reach_AB(Aminus2, Bminus2, new_H.get_flow(locminus1)["var1"], new_H.get_flow(similar_mode), ftube[i - 2], ftube[i - 1], G)

                            Aminus1_cre, Bminus1_cre = lib.reach_AB(Aminus2, Bminus2, new_H.get_flow(locminus1)["var1"], M[i-1], ftube[i - 2], ftube[i - 1], G)

                        else:
                            # Corresponding location in the path at the (i-1)-th position
                            loc0 = new_Hpath[i - 1]
                            locminus1 = new_Hpath[i - 2]

                            G = ppl.NNC_Polyhedron(dim, 'universe')

                            Aminus2 = Aa[i - 3]
                            Bminus2 = Bb[i - 3]

                            if similar_mode != loc0 and similar_mode is not None:
                                Aminus1_mod, Bminus1_mod = lib.reach_AB(Aminus2, Bminus2, new_H.get_flow(locminus1)["var1"],
                                                                        new_H.get_flow(similar_mode)["var1"], ftube[i - 2],
                                                                        ftube[i - 1], G)

                            Aminus1_cre, Bminus1_cre = lib.reach_AB(Aminus2, Bminus2, new_H.get_flow(locminus1)["var1"],
                                                                    M[i - 1], ftube[i - 2], ftube[i - 1], G)


                        # COMPUTE Aa[i-1]

                        if similar_mode != loc0 and similar_mode is not None:

                            G = ppl.NNC_Polyhedron(dim, 'universe')
                            A0, B0 = lib.reach_AB(Aminus1_mod, Bminus1_mod, new_H.get_flow(similar_mode)['var1'], new_H.get_flow(loc1)['var1'], ftube[i - 1], ftube[i], G)
                            mode_action = 'modification'

                            # if A0.is_empty() and B0.is_empty():
                            if B0.is_empty():
                                A0, B0 = lib.reach_AB(Aminus1_cre, Bminus1_cre, M[i - 1], new_H.get_flow(loc1)['var1'], ftube[i - 1], ftube[i], G)
                                mode_action = 'creation'

                        else:

                            G = ppl.NNC_Polyhedron(dim, 'universe')
                            A0, B0 = lib.reach_AB(Aminus1_cre, Bminus1_cre, M[i - 1], new_H.get_flow(loc1)['var1'], ftube[i - 1], ftube[i], G)
                            mode_action = 'creation'

                        # This refers to P[i-1]
                        P0 = ppl.NNC_Polyhedron(A0)
                        P0.poly_hull_assign(B0)

                        if B0.is_empty():
                            raise RuntimeError("B[i-1] is empty!")

                        elif P0.is_empty():
                            raise RuntimeError("P[i-1] is empty!")

                        else:

                            # P[i] not empty with the corresponding location in the path at the (i+1)-th position
                            # Modification or mode creation in the hybrid automaton new_H for the (i+1)-th location in new_Hpath
                            if mode_action == 'modification':

                                Pminus1 = ppl.NNC_Polyhedron(Aminus1_mod)
                                Pminus1.poly_hull_assign(Bminus1_mod)

                                # new_H = modify_mode(new_H, P, ftube[i - 1], ftube[i], locminus1, similar_mode, loc1)
                                new_H = modify_mode(new_H, Pminus1, ftube[i - 1], ftube[i], locminus1, similar_mode, loc1)

                                new_Hpath[i - 1] = similar_mode

                                if i >= 2:
                                    Aa[i - 2] = Aminus1_mod
                                    Bb[i - 2] = Bminus1_mod

                            else:  # mode_action == 'creation'

                                mode = create_name(proposed=loc0 + '_' + str(k), hybrid_automaton=new_H)

                                Pminus1 = ppl.NNC_Polyhedron(Aminus1_cre)
                                Pminus1.poly_hull_assign(Bminus1_cre)

                                # new_H = create_mode(new_H, P, ftube[i - 1], ftube[i], M[i - 1], locminus1, mode, loc1)
                                new_H = create_mode(new_H, Pminus1, ftube[i - 1], ftube[i], M[i - 1], locminus1, mode, loc1)

                                # Redefine the path
                                Hpath[i - 1] = mode

                                if i >= 2:
                                    Aa[i - 2] = Aminus1_cre
                                    Bb[i - 2] = Bminus1_cre

                            Aa[i - 1] = A0
                            Bb[i - 1] = B0

                    else:
                        # P[i] not empty with similar dynamics at the i-th position
                        if mode_action == 'modification':

                            P0 = ppl.NNC_Polyhedron(aux_A_mod)
                            P0.poly_hull_assign(aux_B_mod)

                            if i == maxind:
                                F = ppl.NNC_Polyhedron(dim, 'empty')
                                # new_H = modify_mode(new_H, P, ftube[i], F, loc0, similar_mode, loc2)
                                new_H = modify_mode(new_H, P0, ftube[i], F, loc0, similar_mode, loc2)
                            else:
                                # new_H = modify_mode(new_H, P, ftube[i], ftube[i + 1], loc0, similar_mode, loc2)
                                new_H = modify_mode(new_H, P0, ftube[i], ftube[i + 1], loc0, similar_mode, loc2)

                            new_Hpath[i] = similar_mode

                            if i >= 1:
                                Aa[i - 1] = aux_A_mod
                                Bb[i - 1] = aux_B_mod


                        else:  # mode_action == 'creation'

                            mode = create_name(proposed=loc1 + '_' + str(k), hybrid_automaton=new_H)

                            P0 = ppl.NNC_Polyhedron(aux_A_cre)
                            P0.poly_hull_assign(aux_B_cre)

                            if i == maxind:
                                F = ppl.NNC_Polyhedron(dim, 'empty')
                                # new_H = create_mode(new_H, P, ftube[i], F, M[i], loc0, mode, loc2)
                                new_H = create_mode(new_H, P0, ftube[i], F, M[i], loc0, mode, loc2)
                            else:
                                # new_H = create_mode(new_H, P, ftube[i], ftube[i + 1], M[i], loc0, mode, loc2)
                                new_H = create_mode(new_H, P0, ftube[i], ftube[i + 1], M[i], loc0, mode, loc2)

                            # Redefine the path
                            new_Hpath[i] = mode

                            if i >= 1:
                                Aa[i - 1] = aux_A_cre
                                Bb[i - 1] = aux_B_cre

                        if i >= len(Aa):
                            Aa.append(A)
                            Bb.append(B)
                        else:
                            Aa[i] = A
                            Bb[i] = B

                        i = i + 1


                else:
                    # P[i] not empty with the corresponding location in the path at the i-th position
                    # by modifying the corresponding guard or invariant
                    if mode_action == 'modification':

                        P0 = ppl.NNC_Polyhedron(aux_A)
                        P0.poly_hull_assign(aux_B)

                        if i == maxind:
                            F = ppl.NNC_Polyhedron(dim,'empty')
                            # new_H = modify_mode(new_H, P, ftube[i], F, loc0, loc1, loc2)
                            new_H = modify_mode(new_H, P0, ftube[i], F, loc0, loc1, loc2)
                        else:
                            # new_H = modify_mode(new_H, P, ftube[i], ftube[i + 1], loc0, loc1, loc2)
                            new_H = modify_mode(new_H, P0, ftube[i], ftube[i + 1], loc0, loc1, loc2)

                    else:
                        raise RuntimeError("We reach in here without mode_action equal to modification!")

                    if i >= len(Aa):
                        Aa.append(A)
                        Bb.append(B)
                    else:
                        Aa[i] = A
                        Bb[i] = B

                    i = i + 1

            else:
                # # P[i] not empty with the corresponding location in the path at the (i+1)-th position
                # Modification or mode creation in the hybrid automaton new_H for the (i+1)-th location in new_Hpath

                # We have already assigned loc1 = new_Hpath[i] and loc2 = new_Hpath[i+1]
                if i + 1 == maxind:
                    loc3 = ''
                    final_tube_piece = ppl.NNC_Polyhedron(dim,'empty')
                else:
                    loc3 = new_Hpath[i + 2]
                    final_tube_piece = ftube[i + 2]

                if mode_action == 'modification':
                    # I might be defining loc3 = ''
                    new_H = modify_mode(new_H, P, ftube[i+1], ftube[i+2], loc1, similar_mode, loc3)
                    # Redefine the path
                    new_Hpath[i + 1] = similar_mode


                else:   # mode_action == 'creation'

                    #loc3 = new_Hpath[i + 2]

                    mode = create_name(proposed=loc2 + '_' + str(k), hybrid_automaton=new_H)

                    # new_H = create_mode(new_H, P, ftube[i + 1], ftube[i + 2], M[i + 1], loc1, mode, loc3)
                    new_H = create_mode(new_H, P, ftube[i + 1], final_tube_piece, M[i + 1], loc1, mode, loc3)
                    # Redefine the path
                    new_Hpath[i + 1] = mode

                if i >= len(Aa):
                    Aa.append(A)
                    Bb.append(B)
                else:
                    Aa[i] = A
                    Bb[i] = B

                i = i + 1


        else:
            # P[i] not empty with the corresponding location in the path at the i-th position

            if i >= len(Aa):
                Aa.append(A)
                Bb.append(B)
            else:
                Aa[i] = A
                Bb[i] = B

            i = i + 1

    final_H = modify_ha(H,new_H,new_Hpath)

    return final_H

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------

def modify_ha_wrtpath(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, initial_index, empty_index, max_index):

    dim = hybrid_automaton.dim + 1
    projection_coordinate_list = range(1, dim)

    if empty_index == max_index:
        range_index = empty_index
    else:
        range_index = empty_index + 1

    # for i in range(initial_index, empty_index + 1):
    for i in range(initial_index, range_index):

        new_mode = new_ha_path[i]
        old_mode = ha_path[i]

        # Add all the new modes to the hybrid automaton
        if new_mode != old_mode and new_mode not in hybrid_automaton.locations:

            polyhedron_P_i = lib.convex_hull(A_list[i], B_list[i])
            polyhedron_P_ip1 = lib.convex_hull(A_list[i + 1], B_list[i + 1])

            invariant = lib.projection(lib.convex_hull(polyhedron_P_i, polyhedron_P_ip1), projection_coordinate_list)

            hybrid_automaton = mode_addition(H = hybrid_automaton,
                                             name = new_mode,
                                             inv = invariant,
                                             flow = flow_list[i - initial_index])


    # Modify, if required, all edges and guards associated to the modes in the new path
    # for i in range(initial_index, empty_index):
    for i in range(initial_index, range_index):

        mode = new_ha_path[i]

        polyhedron_P_i = lib.convex_hull(A_list[i], B_list[i])
        polyhedron_P_ip1 = lib.convex_hull(A_list[i + 1], B_list[i + 1])

        invariant = lib.projection(lib.convex_hull(polyhedron_P_i, polyhedron_P_ip1), projection_coordinate_list)

        if i == 0:

            in_edge = None
            in_guard = None

        else:

            previous_mode = new_ha_path[i - 1]

            in_edge = (previous_mode, mode)
            in_guard = lib.projection(polyhedron_P_i, projection_coordinate_list)

        if i + 1 in range(len(new_ha_path)):

            posterior_mode = new_ha_path[i + 1]

            if posterior_mode == None:

                out_edge = None
                out_guard = None

            else:

                out_edge = (mode, posterior_mode)
                out_guard = lib.projection(polyhedron_P_ip1, projection_coordinate_list)

        else:

            out_edge = None
            out_guard = None


        hybrid_automaton = mode_modification(H = hybrid_automaton,
                                             mode_name = mode,
                                             inv = invariant,
                                             in_edge = in_edge,
                                             in_guard = in_guard,
                                             out_edge = out_edge,
                                             out_guard = out_guard)

    return hybrid_automaton




def modify_ha_wrtpath_test(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, initial_index, empty_index, max_index):

    dim = hybrid_automaton.dim + 1
    projection_coordinate_list = range(1, dim)

    if empty_index == max_index:
        range_index = empty_index
    else:
        range_index = empty_index + 1

    # for i in range(initial_index, empty_index + 1):
    for i in range(initial_index, range_index):

        new_mode = new_ha_path[i]
        old_mode = ha_path[i]

        # Add all the new modes to the hybrid automaton
        if new_mode != old_mode and new_mode not in hybrid_automaton.locations:

            polyhedron_P_i = lib.convex_hull(A_list[i], B_list[i])
            polyhedron_P_ip1 = lib.convex_hull(A_list[i + 1], B_list[i + 1])

            invariant = lib.projection(lib.convex_hull(polyhedron_P_i, polyhedron_P_ip1), projection_coordinate_list)

            hybrid_automaton = mode_addition(H = hybrid_automaton,
                                             name = new_mode,
                                             inv = invariant,
                                             # flow = flow_list[i - initial_index])
                                             flow=flow_list[i])


    # Modify, if required, all edges and guards associated to the modes in the new path
    # for i in range(initial_index, empty_index):
    for i in range(initial_index, range_index):

        mode = new_ha_path[i]

        polyhedron_P_i = lib.convex_hull(A_list[i], B_list[i])
        polyhedron_P_ip1 = lib.convex_hull(A_list[i + 1], B_list[i + 1])


        invariant = lib.projection(lib.convex_hull(polyhedron_P_i, polyhedron_P_ip1), projection_coordinate_list)

        if i == 0:

            in_edge = None
            in_guard = None

        else:

            previous_mode = new_ha_path[i - 1]

            in_edge = (previous_mode, mode)
            in_guard = lib.projection(polyhedron_P_i, projection_coordinate_list)

        if i + 1 in range(len(new_ha_path)):

            posterior_mode = new_ha_path[i + 1]

            if posterior_mode == None:

                out_edge = None
                out_guard = None

            else:

                out_edge = (mode, posterior_mode)
                out_guard = lib.projection(polyhedron_P_ip1, projection_coordinate_list)

        else:

            out_edge = None
            out_guard = None


        hybrid_automaton = mode_modification(H = hybrid_automaton,
                                             mode_name = mode,
                                             inv = invariant,
                                             in_edge = in_edge,
                                             in_guard = in_guard,
                                             out_edge = out_edge,
                                             out_guard = out_guard)

    return hybrid_automaton






def repair_ha(empty_index, max_index, pwl_function, pwl_function_slopes, pwl_function_tube, hybrid_automaton, A_list, B_list, polyhedron_P, ha_path, timeseries_order):

    flow_list = []
    new_ha_path = ha_path[:]

    for i in range(empty_index, -1, -1):

        """ Strategy 1: relax guard or invariant for i """
        if i != max_index:
            mode = new_ha_path[i]

            if mode is None:
                flow = None
            else:
                flow = hybrid_automaton.get_flow(mode)
            flow_list.insert(0,flow)

        poly_P, A_list, B_list = nlib.flow_switching_reach_P_index(empty_index,
                                                                   max_index,
                                                                   i,
                                                                   flow_list,
                                                                   A_list,
                                                                   B_list,
                                                                   polyhedron_P,
                                                                   pwl_function,
                                                                   pwl_function_tube)

        if not poly_P.is_empty():
            hybrid_automaton = modify_ha_wrtpath(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, i, empty_index, max_index)
            break

        """ Strategy 2: similar flow for i and pwl_function slope for the posterior indices """
        if i != max_index:

            similar_mode = nlib.ndim_similar_flow_mode(pwl_function[i], pwl_function[i + 1], hybrid_automaton)   # This function can provide similar_mode = None

        else:
            similar_mode = None

        if similar_mode is None:
            similar_flow = None
        else:
            similar_flow = hybrid_automaton.get_flow(similar_mode)

        if similar_flow is not None and similar_mode != new_ha_path[i]:
            new_ha_path[i] = similar_mode

            # similar_flow = hybrid_automaton.get_flow(similar_mode)
            flow_list[0] = similar_flow

            poly_P, A_list, B_list = nlib.flow_switching_reach_P_index(empty_index,
                                                                       max_index,
                                                                       i,
                                                                       flow_list,
                                                                       A_list,
                                                                       B_list,
                                                                       polyhedron_P,
                                                                       pwl_function,
                                                                       pwl_function_tube)


            if not poly_P.is_empty():
                hybrid_automaton = modify_ha_wrtpath(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, i, empty_index, max_index)
                break

        """ Strategy 3: pwl_function slope for i and for the posterior indices """
        if i != max_index:
            new_slope = pwl_function_slopes[i]
        else:
            new_slope = None

        # if new_slope != similar_flow and new_slope != flow:
        if not lib.equal_vectors(new_slope, similar_flow) and not lib.equal_vectors(new_slope,flow):
            new_mode = create_name(proposed='loc' + str(i) + '_' + str(timeseries_order), hybrid_automaton=hybrid_automaton)
            new_ha_path[i] = new_mode

            # Substitute the unsuccesful similar flow by the slope in the PWL function
            flow_list[0] = pwl_function_slopes[i]

            poly_P, A_list, B_list = nlib.flow_switching_reach_P_index(empty_index,
                                                                       max_index,
                                                                       i,
                                                                       flow_list,
                                                                       A_list,
                                                                       B_list,
                                                                       polyhedron_P,
                                                                       pwl_function,
                                                                       pwl_function_tube)

            if not poly_P.is_empty():
                hybrid_automaton = modify_ha_wrtpath(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, i, empty_index, max_index)
                break

    return hybrid_automaton, new_ha_path, A_list, B_list




def repair_ha_test(empty_index, max_index, pwl_function, pwl_function_slopes, pwl_function_tube, hybrid_automaton, A_list, B_list, polyhedron_P, ha_path, data_index):

    flow_list = []
    new_ha_path = ha_path[:]

    for i in range(empty_index):
        flow_list.append(hybrid_automaton.get_flow(new_ha_path[i]))
    for i in range(empty_index,max_index):
        flow_list.append(None)

    for i in range(empty_index, -1, -1):

        """ Strategy 1: relax guard or invariant for i """
        if i != max_index:
            mode = new_ha_path[i]

            if mode is None:
                flow = None
            else:
                flow = hybrid_automaton.get_flow(mode)
            # flow_list.insert(0,flow)
            flow_list[i] = flow

        poly_P, A_list, B_list = nlib.flow_switching_reach_P_index_test(empty_index,
                                                                   max_index,
                                                                   i,
                                                                   flow_list,
                                                                   A_list,
                                                                   B_list,
                                                                   polyhedron_P,
                                                                   pwl_function,
                                                                   pwl_function_tube)

        if not poly_P.is_empty():
            hybrid_automaton = modify_ha_wrtpath_test(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, i, empty_index, max_index)
            break

        """ Strategy 2: similar flow for i and pwl_function slope for the posterior indices """
        if i != max_index:

            similar_mode = nlib.ndim_similar_flow_mode(pwl_function[i], pwl_function[i + 1], hybrid_automaton)   # This function can provide similar_mode = None

        else:
            similar_mode = None

        if similar_mode is None:
            similar_flow = None
        else:
            similar_flow = hybrid_automaton.get_flow(similar_mode)

        if similar_flow is not None and similar_mode != new_ha_path[i]:
            new_ha_path[i] = similar_mode

            # similar_flow = hybrid_automaton.get_flow(similar_mode)
            # flow_list[0] = similar_flow
            flow_list[i] = similar_flow

            poly_P, A_list, B_list = nlib.flow_switching_reach_P_index_test(empty_index,
                                                                       max_index,
                                                                       i,
                                                                       flow_list,
                                                                       A_list,
                                                                       B_list,
                                                                       polyhedron_P,
                                                                       pwl_function,
                                                                       pwl_function_tube)


            if not poly_P.is_empty():
                hybrid_automaton = modify_ha_wrtpath_test(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, i, empty_index, max_index)
                break

        """ Strategy 3: pwl_function slope for i and for the posterior indices """
        if i != max_index:
            new_slope = pwl_function_slopes[i]
        else:
            new_slope = None

        # if new_slope != similar_flow and new_slope != flow:
        if not lib.equal_vectors(new_slope, similar_flow) and not lib.equal_vectors(new_slope,flow):
            new_mode = create_name(proposed='loc' + str(i) + '_' + str(data_index), hybrid_automaton=hybrid_automaton)
            new_ha_path[i] = new_mode

            # Substitute the unsuccesful similar flow by the slope in the PWL function
            # flow_list[0] = pwl_function_slopes[i]
            flow_list[i] = pwl_function_slopes[i]

            poly_P, A_list, B_list = nlib.flow_switching_reach_P_index_test(empty_index,
                                                                       max_index,
                                                                       i,
                                                                       flow_list,
                                                                       A_list,
                                                                       B_list,
                                                                       polyhedron_P,
                                                                       pwl_function,
                                                                       pwl_function_tube)

            if not poly_P.is_empty():
                hybrid_automaton = modify_ha_wrtpath_test(hybrid_automaton, A_list, B_list, ha_path, new_ha_path, flow_list, i, empty_index, max_index)
                break

    return hybrid_automaton, new_ha_path, A_list, B_list







def adaptation_ha(pwl_function, pwl_f_tube, A_list, B_list, hybrid_automaton, ha_path, empty_index, data_index):
    """ Obtain a hybrid automaton such that it captures the behaviour of the
	PWL function f.
	------------------------------------------------------------------------------------
	input:	pwl_function		List of points: PWL function	list of list
			pwl_f_tube			List of polyhedra				list of ppl.NNC_Polyhedron
			A_list				List of j polyhedra				list of ppl.NNC_Polyhedron
			B_list				List of j polyhedra				list of ppl.NNC_Polyhedron
			hybrid_automaton    Hybrid automaton				HybridSystemABC
			ha_path			    List of locations				list of HybridSystemABC.locations
			empty_index		    Index for emptiness				integer
			timeseries_order	k-th time series				integer

	output:	new_H			Hybrid automaton		HybridSystemABC. """


    dim = hybrid_automaton.dim + 1

    # Auxiliary hybrid automaton
    aux_hybrid_automaton = hybrid_automaton.copy()
    # Auxiliary ha_path
    aux_ha_path = ha_path[:]

    # Compute slopes of the PWL function f
    pwl_function_slopes = lib.slopes(pwl_function)

    max_index = len(ha_path)
    for i in range(empty_index, max_index + 1):

        if i == 0:
            previous_poly_P = ppl.NNC_Polyhedron(dim, 'empty')

        else:
            previous_poly_P = lib.convex_hull(A_list[i - 1], B_list[i - 1])

        poly_A, poly_B = nlib.ha_switching_reach_AB(i, max_index, previous_poly_P, hybrid_automaton, aux_ha_path, pwl_function, pwl_f_tube)
        poly_P = lib.convex_hull(poly_A, poly_B)

        if poly_P.is_empty():

            # aux_hybrid_automaton, aux_ha_path, A_list, B_list = repair_ha(i,
            #                                                               max_index,
            #                                                               pwl_function,
            #                                                               pwl_function_slopes,
            #                                                               pwl_f_tube,
            #                                                               aux_hybrid_automaton,
            #                                                               A_list,
            #                                                               B_list,
            #                                                               poly_P,
            #                                                               aux_ha_path,
            #                                                               timeseries_order)

            aux_hybrid_automaton, aux_ha_path, A_list, B_list = repair_ha_test(i,
                                                                               max_index,
                                                                               pwl_function,
                                                                               pwl_function_slopes,
                                                                               pwl_f_tube,
                                                                               aux_hybrid_automaton,
                                                                               A_list,
                                                                               B_list,
                                                                               poly_P,
                                                                               aux_ha_path,
                                                                               data_index)




        else:
        #
        #     if i >= len(A_list):
        #         A_list.append(poly_A)
        #         B_list.append(poly_B)
        #     else:
        #         A_list[i] = poly_A
        #         B_list[i] = poly_B
            A_list[i] = poly_A
            B_list[i] = poly_B

        hybrid_automaton = modify_ha(hybrid_automaton, aux_hybrid_automaton, aux_ha_path[:i+1])

    return hybrid_automaton



