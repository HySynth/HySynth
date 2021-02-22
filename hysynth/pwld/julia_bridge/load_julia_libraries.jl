using LazySets, MathematicalSystems, Optim, Random, LinearAlgebra
import Distributions, Polyhedra, CDDLib, DifferentialEquations
using LazySets: dim, HalfSpace, sample, basetype

# use Reachability or ReachabilityAnalysis library depending on Julia version
const USE_REACHABILITY = (VERSION < v"1.3")
if USE_REACHABILITY
    using Reachability
else
    using ReachabilityAnalysis
end

include("AffDyn.jl")

include("julia_library.jl")

include("time_series_to_symbolic.jl")

include("analyze_sequence.jl")
