struct AffDyn{MT<:AbstractMatrix{Float64}, VT<:AbstractVector{Float64}}
    A::MT
    b::VT
end

function Base.:(-)(dyn::AffDyn)
    return AffDyn(-dyn.A, -dyn.b)
end
