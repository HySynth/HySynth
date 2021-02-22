function reset_seed(seed)
    Random.seed!(seed)
end

function basetype_string(set::LazySet)
    return string(basetype(set))
end

function flatten_dyn(dyn)
    return dyn.A(), dyn.b()
end

function flatten_dyn(dyn::AffDyn)
    return dyn.A, dyn.b
end

function flatten_Interval(I)
    I = convert(Interval, I)
    return min(I), max(I)
end

function flatten_BallInf(B)
    B = convert(BallInf, B)
    return B.center, B.radius
end

function flatten_Hyperrectangle(H)
    H = convert(Hyperrectangle, H)
    return H.center, H.radius
end

function flatten_HalfSpace(hs)
    hs = convert(HalfSpace, hs)
    return hs.a, hs.b
end

function flatten_HPolyhedron(P)
    P = convert(HPolyhedron, P)
    return P.constraints
end

function flatten_VPolygon(P)
    P = convert(VPolygon, P)
    return P.vertices
end

function successor(b::AbstractVector, t, x0)
    result = x0 + b * t
    return result
end

function successor(A::AbstractMatrix, t, x0)
    result = exp(A * t) * x0
    return result
end

function successor(dyn::AffDyn, t, x0)
    if iszero(dyn.A)
        return successor(dyn.b, t, x0)
    elseif iszero(dyn.b)
        return successor(dyn.A, t, x0)
    end
    # affine solution that only works for invertible matrix
#    try
#        inv_A = inv(dyn.A)
#        id = Diagonal(ones(n))
#        result = exp(dyn.A * t) * x0 + (exp(dyn.A * t) - id) * inv_A * dyn.b
#        return result
#    catch e
#        # A not invertible
#        # return nothing
#    end
    # make affine system linear by extending the dimension
    A_high = [dyn.A dyn.b; zeros(length(dyn.b) + 1)']
    x1_high = successor(A_high, t, vcat(x0, 1.0))
    x1 = x1_high[1:end-1]
    return x1
end

function successor(b::AbstractVector, time, P0::LazySet)
    offset = b * time
    P1 = translate(P0, offset)
    return P1
end

function successor(A::AbstractMatrix, time, P0::LazySet)
    B = exp(A * time)
    P1 = linear_map(B, P0)
    return P1
end

function successor(dyn::AffDyn, time, P0::LazySet)
    # make affine system linear by extending the dimension
    n = length(dyn.b)
    A_high = [dyn.A dyn.b; zeros(n + 1)']
    if n == 1
        # 1D case can be solved more efficiently and with numerical stability
        P0_itv = convert(Interval, P0)
        l = low(P0_itv)[1]
        u = high(P0_itv)[1]
        P0_high = Hyperrectangle(low=[l, 1.0], high=[u, 1.0])
        P1_high = successor(A_high, time, P0_high)
        P1 = LazySets.project(P1_high, 1:n)
        P1 = convert(Interval, P1)
    else
        one = Interval(1.0 - 1e-5, 1.0 + 1e-5)
        # one = Singleton([1.0])
        P0_high = CartesianProduct(P0, one)
        P1_high = successor(A_high, time, P0_high)
        P1_high = LazySets.normalize(P1_high)
        P1 = LazySets.project(P1_high, 1:n)
        P1 = LazySets.normalize(P1)
    end
    return P1
end

function is_similar_flow(P0, dyn, P1, time; return_set::Bool=false)
    Q1 = successor(dyn, time, P0)
    if return_set
        return !isdisjoint(P1, Q1), Q1
    else
        return !isdisjoint(P1, Q1)
    end
end

function contains(X::LazySet, point::AbstractVector)
    return point ∈ X
end

function polytope_hull(X, Y)
    return convex_hull(X, Y)
end

function get_ivp(b::AbstractVector, X0)
    problem = @ivp(x' = b, x(0) ∈ X0)
    return problem
end

function get_ivp(A::AbstractMatrix, X0)
    problem = @ivp(x' = Ax, x(0) ∈ X0)
    return problem
end

function get_ivp(dyn::AffDyn, X0)
    A = dyn.A
    b = dyn.b
    problem = @ivp(x' = Ax + b, x(0) ∈ X0)
    return problem
end

function compute_reach_tube_hull(dyn, X0::LazySet, time_horizon,
                                 time_step::Number=1e-3, oa=Hyperrectangle)
    problem = get_ivp(dyn, X0)
    if USE_REACHABILITY
        sets = compute_reach_tube_hull_Reachability(problem, time_horizon,
            time_step)
    else
        n = dim(X0)
        sets = compute_reach_tube_hull_ReachabilityAnalysis(problem,
            time_horizon, time_step, n)
    end
    hull = overapproximate(ConvexHullArray(sets), oa)
    return hull
end

function compute_reach_tube_hull_Reachability(problem, time_horizon, time_step)
    options = Options(:T => time_horizon)
    algorithm = BFFPSV18(:δ => time_step)
    solution = Reachability.solve(problem, options; op=algorithm)
    flowpipe = solution.flowpipes[1]
    sets = [Reachability.set(rs) for rs in flowpipe.reachsets]
    return sets
end

function compute_reach_tube_hull_ReachabilityAnalysis(problem, time_horizon,
                                                      time_step, n)
    algorithm = BOX(δ=time_step)
    solution = ReachabilityAnalysis.solve(problem, T=time_horizon, algorithm)
    flowpipe = solution.F
    sets = [ReachabilityAnalysis.set(rs) for rs in ReachabilityAnalysis.array(flowpipe)]
    return sets
end

function getInterval(lo, hi)
    return Interval(lo, hi)
end

function getBallInf(center, radius)
    return BallInf(center, radius)
end

function getHyperrectangle(center, radius)
    return Hyperrectangle(center, radius)
end

function getHalfSpace(a, b)
    return HalfSpace(a, b)
end

function getHPolyhedron(constraints)
    return HPolyhedron(constraints)
end

function getUniverse(dimension)
    return Universe(dimension)
end
