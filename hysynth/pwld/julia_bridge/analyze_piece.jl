# using LazySets

include("necessary_check.jl")
include("sufficient_check.jl")
include("refinement.jl")

function analyze_piece(dyn1, dyn2, x0::AbstractVector{N}, P0::LazySet,
                       ε::Number, time, m::Integer, ζ::Number, compute_ua::Bool;
                       log::Bool=false) where {N}
    dim = length(x0)
    T = time[2] - time[1]

    # necessary check
    P1_oa = check_necessary(dyn1, dyn2, x0, P0, ε, T, m; log=log)
    if !compute_ua
        return P1_oa
    elseif P1_oa isa EmptySet
        if log
            println("no solution exists")
        end
        return EmptySet{N}(dim), EmptySet{N}(dim), Vector{Vector{Float64}}(), x0
    end

    # invert system
    dyn1⁻ = -dyn1
    dyn2⁻ = -dyn2
    x1 = successor(dyn1, T, x0)

    # check sufficient criterion for all corners
    vertices = vertices_list(P1_oa)
    vertices_sat, vertices_unsat =
        check_sufficient_points(dyn1⁻, dyn2⁻, x1, vertices, time, ε; log=log)

    # refinement
    refine!(vertices_sat, P1_oa, vertices_unsat, ζ, dyn1⁻, dyn2⁻, x1, time, ε;
            log=log)

    if isempty(vertices_sat)
        P1_ua = EmptySet{N}(dim)
    else
        P1_ua = VPolytope(vertices_sat)
    end
    return P1_ua, P1_oa, vertices_unsat, x1
end
