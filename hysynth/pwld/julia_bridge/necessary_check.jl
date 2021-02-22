# using LazySets

□(x0, ε) = BallInf(x0, ε)

# general version for affine dynamics
function check_necessary(dyn1, dyn2, x0::AbstractVector{N}, P0::LazySet,
                         ε::Number, T::Number, m::Integer;
                         return_sets::Bool=false, log::Bool=false) where {N}
    if log
        println("running necessary check with $m iterations")
    end

    δ = T / m
    if return_sets
        Bs = Vector{LazySet{N}}()
        Ps = Vector{LazySet{N}}()
        push!(Bs, P0)
        push!(Ps, P0)
        P_last = P0
    end
    j_abort = m
    for j in 1:m
        # if log
        #     println("iteration $j")
        # end
        B = □(successor(dyn1, j * δ, x0), ε)
        P1 = successor(dyn2, δ, P0)
        P0 = intersection(P1, B)
        if return_sets
            push!(Bs, B)
            push!(Ps, P0)
        end
        if P0 isa EmptySet
            j_abort = j
            if return_sets
                P_last = P1
            end
            break
        end
    end
    if log
        println("finished necessary check after $j_abort iterations")
    end
    if return_sets
        return j_abort, P_last, Bs, Ps
    else
        return P0
    end
end

# more efficient version for linear dynamics
function check_necessary(A::AbstractMatrix{N}, B::AbstractMatrix{N},
                         x0::AbstractVector{N}, P0::LazySet, ε::Number,
                         T::Number, m::Integer;
                         return_sets::Bool=false, log::Bool=false) where {N}
    if log
        println("running necessary check with $m iterations")
    end

    δ = T / m
    Φ = exp(A * δ)
    Ψ = exp(B * δ)
    if return_sets
        Bs = Vector{LazySet{N}}()
        Ps = Vector{LazySet{N}}()
        push!(Bs, P0)
        push!(Ps, P0)
        P_last = P0
    end
    j_abort = m
    for j in 1:m
        # if log
        #     println("iteration $j")
        # end
        B = □(Φ^j * x0, ε)
        P1 = linear_map(Ψ, P0)
        P0 = intersection(P1, B)
        if return_sets
            push!(Bs, B)
            push!(Ps, P0)
        end
        if P0 isa EmptySet
            j_abort = j
            if return_sets
                P_last = P1
            end
            break
        end
    end
    if log
        println("finished necessary check after $j_abort iterations")
    end
    if return_sets
        return j_abort, P_last, Bs, Ps
    else
        return P0
    end
end
