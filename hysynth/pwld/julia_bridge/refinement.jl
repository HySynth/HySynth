function refine(P::LazySet, ζ::Number)
    constraints = Vector{HalfSpace{Float64, Vector{Float64}}}()
    for c in constraints_list(P)
        c_tightened = HalfSpace(c.a, c.b - (ζ * norm(c.a, 2)))
        push!(constraints, c_tightened)
    end
    return HPolytope(constraints)
end

function refine!(vertices_sat, P::LazySet, vertices_unsat, ζ::Number,
                 dyn1⁻, dyn2⁻, x1, time, ε; log::Bool=false)
    if !isempty(vertices_unsat)
        while true
            P = refine(P, ζ)
            vertices = vertices_list(P)
            vertices_sat2, vertices_unsat2 =
                check_sufficient_points(dyn1⁻, dyn2⁻, x1, vertices, time, ε; log=log)
            append!(vertices_sat, vertices_sat2)
            if isempty(vertices_unsat2)
                break
            end
            if log
                println("refinement continues")
            end
        end
    end
    return vertices_sat
end
