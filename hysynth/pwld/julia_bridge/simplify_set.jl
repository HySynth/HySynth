# using LazySets

function simplify_overapprox(P::LazySet)
    return overapproximate(P, Zonotope, OctDirections(dim(P)))
end

function simplify_underapprox(P::LazySet; ignore::Bool=false)
    if ignore || P isa EmptySet
        return P
    end
    return underapproximate(P, OctDirections(dim(P)))
end
