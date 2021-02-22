from hysynth.utils.hybrid_system import HybridSystemNoConstraints
from hysynth.pwl.membership.parma_mem import path_membership_info
from hysynth.pwl.hakimi_pwl.unroll_hakimi import unroll_hakimi, get_heuristic_path
import hysynth.pwl.library as lib
import ppl


def relax_ha(pwl_f, hybrid_automaton, ftube):
    """
    Determine if a relaxation of the constraints along any path in a hybrid automaton makes a given PWL function a
    δ-member, and if so, modify the automaton by relaxing the constraints accordingly.

    :param pwl_f: PWL function to check relaxed membership for
    :param hybrid_automaton: hybrid automaton
    :return: a relaxed automaton if successful, and `None` otherwise
    """

    time_horizon = pwl_f[-1][0]

    # automaton with relaxed constraints
    relaxed_automaton = HybridSystemNoConstraints(hybrid_automaton)

    heur_path, success = get_heuristic_path(pwl_path=pwl_f, hybrid_automaton=hybrid_automaton)
    if not success:
        # no path of the corresponding length exists
        return None

    heur_checked = False

    for hybrid_automaton_path in unroll_hakimi(hybrid_system=hybrid_automaton, hakimi_path=pwl_f):

        answer, _, Aa, Bb, _ = path_membership_info(pwl_path=pwl_f,
                                                    hybrid_automaton_path=hybrid_automaton_path,
                                                    hybrid_automaton=relaxed_automaton,
                                                    ftube=ftube)
        if heur_checked is False:
            # this is a very very dirty hack
            answer_heur, _, Aa_heur, Bb_heur, _ = path_membership_info(pwl_path=pwl_f,
                                                                       hybrid_automaton_path=heur_path,
                                                                       hybrid_automaton=relaxed_automaton,
                                                                       ftube=ftube)
            # trigger the flag
            heur_checked = True

            if answer_heur is True:
                hybrid_automaton_path = heur_path
                # relaxation worked
                answer, Aa, Bb = answer_heur, Aa_heur, Bb_heur

        if not answer:
            # relaxation does not work
            continue

        # relaxation worked
        result = hybrid_automaton.copy()
        last_index = len(hybrid_automaton_path)-1
        n = len(pwl_f[0])
        one__to__n_minus_one = range(1, n)
        for j in range(0, last_index+1):
            loc = hybrid_automaton_path[j]
            # obtain left set
            left = ppl.NNC_Polyhedron(Aa[j])
            left.poly_hull_assign(Bb[j])
            # obtain right set
            right = ppl.NNC_Polyhedron(Aa[j + 1])
            right.poly_hull_assign(Bb[j + 1])
            # project away the time dimension
            left = lib.projection(left, one__to__n_minus_one)
            right = lib.projection(right, one__to__n_minus_one)

            # relax_ha invariant
            invariant = ppl.NNC_Polyhedron(result.get_invariant(loc))
            invariant.poly_hull_assign(left)
            invariant.poly_hull_assign(right)
            result.set_invariant(loc, invariant)
            if j < last_index:
                # relax_ha guard
                loc_target = hybrid_automaton_path[j + 1]
                transition = (loc, loc_target)
                guard = ppl.NNC_Polyhedron(result.get_guard(transition))
                guard.poly_hull_assign(right)
                result.set_guard(transition, guard)
                # update the target location's invariant
                invariant = ppl.NNC_Polyhedron(result.get_invariant(loc_target))
                invariant.poly_hull_assign(guard)
                result.set_invariant(loc_target, invariant)
        return result

    # no path relaxation succeeded
    return None
