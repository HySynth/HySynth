from cvxopt import matrix, spmatrix
from cvxopt.solvers import lp


def membership(f, automaton, path, delta, w_inv=1.0, w_grd=1.0, solver='glpk'):
    """
    Check whether a function is δ-close to a path in a hybrid automaton, potentially after increasing invariants and
    guards.
    More precisely, compute the minimum amount by which invariants and guards need to be increased such that the goal is
    achieved, or find out that no such values exist.

    :param f: PWL function, represented as a mapping "piece index (shifted by -1) ↦ (time point, value)"
    :param automaton: hybrid automaton; provides "get_flow(l)", get_invariant(l), and "get_guard(s, t)"
    :param path: path in automaton, represented as a mapping "loc index ↦ (invariant, flow)"
    :param delta: nonnegative number; value of δ
    :param w_inv: nonnegative number; default: 1; weight of invariant changes
    :param w_grd: nonnegative number; default: 1; weight of guard changes
    :param solver: string; solver backend; default: 'glpk'; ∈ [None (= CVXOPT built-in solver), 'glpk', 'mosek', 'dsdp']
    :return: False or a mapping "variable name ↦ value by which the invariant/guard of that name needs to be increased".
             The variable names are "ι⁻_i", "ι⁺_i", "g⁻_i", and "g⁺_i", where ⁻/⁺ stand for lower/upper bounds,
             respectively, and ι/g stand for invariant/guard constraints, respectively.
             Note that the mapping contains values for other variable names as well, but they should be ignored.
    """
    # number of pieces
    m = len(f) - 1

    # number of variables in the linear program
    n = (m + 1 +  # ξ(t_i) for t_0, ..., t_m
         2 * m +  # ι⁻_i, ι⁺_i for i = 1, ..., m
         2 * (m - 1))  # g⁻_i, g⁺_i for i = 1, ..., m-1

    # number of constraints in the linear program
    c = (2 +  # "initially δ-close"
         2 * m +  # "otherwise δ-close"
         4 * m +  # "invariant convex"
         2 * (m - 1) +  # "guard"
         2 * m +  # "flow PWL"
         4 * (m - 1) +  # guard ⊆ invariants
         2 * m +  # invariant additions nonnegative
         2 * (m - 1))  # guard additions nonnegative

    # create mapping from variable symbols to indices
    s2i = dict()  # name ↦ index
    j = 0  # marker for current variable index
    # m+1 symbols ξ(t_i)
    for i in range(0, m+1):
        s2i["ξ(t_{0})".format(i)] = j
        j += 1
    # m symbols ι⁻_i, m symbols ι⁺_i
    for i in range(1, m+1):
        s2i["ι⁻_{0}".format(i)] = j
        j += 1
        s2i["ι⁺_{0}".format(i)] = j
        j += 1
    # m-1 symbols g⁻_i, m-1 symbols g⁺_i
    for i in range(1, m):
        s2i["g⁻_{0}".format(i)] = j
        j += 1
        s2i["g⁺_{0}".format(i)] = j
        j += 1

    assert n == len(s2i), "wrong number of variables: got {0}, expected {1}".format(len(s2i), n)

    # create mapping from constant symbols to values
    s2v = dict()  # name ↦ value
    # first time point is 0
    s2v["t_0"] = float(f[0][0])
    s2v["f(t_0)"] = float(f[0][1])

    for i in range(1, m + 1):
        # i-th location
        loc = path[i-1]
        f_i = f[i]
        f_im1 = f[i-1]
        # intermediate switching times for f
        s2v["t_{0}".format(i)] = float(f_i[0])
        # values of f at switching times for f
        s2v["f(t_{0})".format(i)] = float(f_i[1])
        # slopes of f
        s2v["s^f_{0}".format(i)] = float(f_i[1] - f_im1[1]) / float(f_i[0] - f_im1[0])
        # slopes of ξ
        flow = automaton.get_flow(loc)
        flow = flow._flowtube_store[flow.variables[0]]
        s2v["s^ξ_{0}".format(i)] = float(flow.slope)
        # invariants (lower and upper bounds)
        inv = automaton.get_invariant(loc)
        # unpack guard
        inv = inv._boundary_store[inv.variables[0]]
        s2v["I⁺_{0}".format(i)] = float(inv.upper)
        s2v["I⁻_{0}".format(i)] = float(inv.lower)
    source_loc = path[0]
    for i in range(1, m):
        # i-th guard (lower and upper bounds)
        target_loc = path[i]
        guard = automaton.get_guard((source_loc, target_loc))
        # unpack guard
        guard = guard._boundary_store[guard.variables[0]]
        s2v["G⁺_{0}".format(i)] = float(guard.upper)
        s2v["G⁻_{0}".format(i)] = float(guard.lower)
        source_loc = target_loc

    # -- define some helper functions --

    mat = spmatrix(0.0, [], [], (c, n))
    vec = matrix(0.0, (c, 1))

    # write the value of a constant at the index of a variable (symbol)
    def write(si, v, k):
        mat[k, s2i[si]] = v

    # add two constraints for a value ξ being in the δ interval around f
    def addconstraint_delta_tube(xi, f, k):
        f_val = s2v[f]
        # lower bound (ξ ≥ f - δ ≡ -ξ ≤ -(f - δ))
        write(xi, -1.0, k)
        vec[k, 0] = -(f_val - delta)
        k += 1
        # upper bound (ξ ≤ f + delta)
        write(xi, 1.0, k)
        vec[k, 0] = f_val + delta
        k += 1
        return k

    # add two constraints for a variable being in a (constant) interval
    def addconstraint_interval(var, lval, lvar, uval, uvar, k):
        # lower bound (x ≥ c - l ≡ -x - l ≤ -c)
        write(var, -1.0, k)
        write(lvar, -1.0, k)
        vec[k, 0] = -s2v[lval]
        k += 1
        # upper bound (x ≤ c + u ≡ x - u ≤ c)
        write(var, 1.0, k)
        write(uvar, -1.0, k)
        vec[k, 0] = s2v[uval]
        k += 1
        return k

    # add two constraints for fixing the successor value by following the flow
    def addconstraint_flow(i, k):
        xi_t_i = "ξ(t_{0})".format(i)
        xi_t_im1 = "ξ(t_{0})".format(i-1)
        delta_t = s2v["t_{0}".format(i)] - s2v["t_{0}".format(i-1)]
        s = s2v["s^ξ_{0}".format(i)]
        offset = delta_t * s
        # express equality (ξ(t_i) = ξ(t_{i-1}) + Δ_t ⋅ s^ξ_i) as lower and upper bound
        # lower bound (ξ(t_i) ≤ ξ(t_{i-1}) + Δ_t ⋅ s^ξ_i ≡ ξ(t_i) - ξ(t_{i-1}) ≤ Δ_t ⋅ s^ξ_i)
        write(xi_t_i, 1.0, k)
        write(xi_t_im1, -1.0, k)
        vec[k, 0] = offset
        k += 1
        # upper bound (ξ(t_i) ≥ ξ(t_{i-1}) + Δ_t ⋅ s^ξ_i ≡ -ξ(t_i) + ξ(t_{i-1}) ≤ -(Δ_t ⋅ s^ξ_i))
        write(xi_t_i, -1.0, k)
        write(xi_t_im1, 1.0, k)
        vec[k, 0] = -offset
        k += 1
        return k

    # add four constraints to keep the guard inside the invariant
    def addconstraint_guard_subset_invariants(i, k):
        gm = "g⁻_{0}".format(i)
        gp = "g⁺_{0}".format(i)
        v_grd_m = s2v["G⁻_{0}".format(i)]
        v_grd_p = s2v["G⁺_{0}".format(i)]
        # lower bound predecessor invariant (G⁻_i - g⁻_i ≥ I⁻_i - ι⁻_i ≡ g⁻_i - ι⁻_i ≤ G⁻_i - I⁻_i)
        write(gm, 1.0, k)
        write("ι⁻_{0}".format(i), -1.0, k)
        vec[k, 0] = v_grd_m - s2v["I⁻_{0}".format(i)]
        k += 1
        # upper bound predecessor invariant (G⁺_i + g⁺_i ≤ I⁺_i + ι⁺_i ≡ g⁺_i - ι⁺_i ≤ I⁺_i - G⁺_i)
        write(gp, 1.0, k)
        write("ι⁺_{0}".format(i), -1.0, k)
        vec[k, 0] = s2v["I⁺_{0}".format(i)] - v_grd_p
        k += 1
        # lower bound successor invariant
        # (G⁻_i - g⁻_i ≥ I⁻_{i+1} - ι⁻_{i+1} ≡ g⁻_i - ι⁻_{i+1} ≤ G⁻_i - I⁻_{i+1})
        write(gm, 1.0, k)
        write("ι⁻_{0}".format(i + 1), -1.0, k)
        vec[k, 0] = v_grd_m - s2v["I⁻_{0}".format(i + 1)]
        k += 1
        # upper bound successor invariant
        # (G⁺_i + g⁺_i ≤ I⁺_{i+1} + ι⁺_{i+1} ≡ g⁺_i - ι⁺_{i+1} ≤ I⁺_{i+1} - G⁺_i)
        write(gp, 1.0, k)
        write("ι⁺_{0}".format(i + 1), -1.0, k)
        vec[k, 0] = s2v["I⁺_{0}".format(i + 1)] - v_grd_p
        k += 1
        return k

    # add two constraints to enforce nonnegative invariant additions
    def addconstraint_invariant_addition_nonneg(i, k):
        write("ι⁻_{0}".format(i), -1.0, k)
        # vec[k, 0] = 0.0 # commented because the entry is already 0
        k += 1
        write("ι⁺_{0}".format(i), -1.0, k)
        # vec[k, 0] = 0.0 # commented because the entry is already 0
        k += 1
        return k

    # add two constraints to enforce nonnegative guard additions
    def addconstraint_guard_addition_nonneg(i, k):
        write("g⁻_{0}".format(i), -1.0, k)
        # vec[k, 0] = 0.0 # commented because the entry is already 0
        k += 1
        write("g⁺_{0}".format(i), -1.0, k)
        # vec[k, 0] = 0.0 # commented because the entry is already 0
        k += 1
        return k

    # -- create constraints --

    k = 0  # marker for current constraint index

    # initially δ-close
    k = addconstraint_delta_tube("ξ(t_0)", "f(t_0)", k)  # +2

    # otherwise δ-close
    for i in range(1, m+1):
        k = addconstraint_delta_tube("ξ(t_{0})".format(i), "f(t_{0})".format(i), k)  # +2

    # invariant convex
    for i in range(1, m+1):
        inv_bound_m = "I⁻_{0}".format(i)
        inv_bound_p = "I⁺_{0}".format(i)
        iota_m = "ι⁻_{0}".format(i)
        iota_p = "ι⁺_{0}".format(i)
        k = addconstraint_interval("ξ(t_{0})".format(i-1), inv_bound_m, iota_m, inv_bound_p, iota_p,
                                   k)  # +2
        k = addconstraint_interval("ξ(t_{0})".format(i), inv_bound_m, iota_m, inv_bound_p, iota_p,
                                   k)  # +2

    # guard
    for i in range(1, m):
        k = addconstraint_interval("ξ(t_{0})".format(i), "G⁻_{0}".format(i), "g⁻_{0}".format(i),
                                   "G⁺_{0}".format(i), "g⁺_{0}".format(i), k)  # +2

    # flow PWL
    for i in range(1, m+1):
        k = addconstraint_flow(i, k)  # +2

    # guard ⊆ invariants
    for i in range(1, m):
        k = addconstraint_guard_subset_invariants(i, k)  # +4

    # invariant additions nonnegative
    for i in range(1, m+1):
        k = addconstraint_invariant_addition_nonneg(i, k)  # +2

    # guard additions nonnegative
    for i in range(1, m):
        k = addconstraint_guard_addition_nonneg(i, k)  # +2

    assert c == k, "wrong number of constraints: got {0}, expected {1}".format(k, c)

    # -- set up and solve linear program --

    obj = matrix(0.0, (n, 1))
    for i in range(1, m+1):
        obj[s2i["ι⁻_{0}".format(i)]] = w_inv
        obj[s2i["ι⁺_{0}".format(i)]] = w_inv
    for i in range(1, m):
        obj[s2i["g⁻_{0}".format(i)]] = w_grd
        obj[s2i["g⁺_{0}".format(i)]] = w_grd

    # solve linear program
    lp_result = lp(obj, mat, vec, solver=solver)
    if lp_result['status'] == 'optimal':
        print("path is δ-close when relaxing the constraints")
        sol = lp_result['x']
    elif lp_result['status'] == 'primal infeasible':
        print("path is NOT δ-close, even when relaxing the constraints")
        sol = None
    else:
        assert False, "LP solver returned with status {0}".format(lp_result.status)

    # debug output
#     print(lp_result)
#     if sol is not None:
#         for i in range(1, n+1):
#             for (k, v) in s2i.items():
#                 if v == i:
#                     print("{0} == {1}".format(k, sol[v]))
#                     break
    return sol
