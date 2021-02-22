# using Optim
# import DifferentialEquations

# ODE system for affine dynamics
function check_sufficient_ode_function(dyn1::AffDyn, dyn2::AffDyn)
    A1 = dyn1.A
    b1 = dyn1.b
    A2 = dyn2.A
    b2 = dyn2.b
    n = length(b1)
    Z = zeros(n, n)
    C = [A1 Z Z; Z A2 Z; A1 -A2 Z]
    d = [b1; b2; b1-b2]
    h(u, p, t) = C * u + d
    return h, n
end

# ODE system for mixed affine and linear dynamics
function check_sufficient_ode_function(dyn1::AffDyn, B::AbstractMatrix)
    n = size(B, 1)
    dyn2 = AffDyn(B, zeros(n))
    return check_sufficient_ode_function(dyn1, dyn2)
end
function check_sufficient_ode_function(A::AbstractMatrix, dyn2::AffDyn)
    n = size(A, 1)
    dyn1 = AffDyn(A, zeros(n))
    return check_sufficient_ode_function(dyn1, dyn2)
end

# ODE system for linear dynamics
function check_sufficient_ode_function(A::AbstractMatrix, B::AbstractMatrix)
    n = size(A, 1)
    Z = zeros(n, n)
    C = [A Z Z; Z B Z; A -B Z]
    h(u, p, t) = C * u
    return h, n
end

function check_sufficient(dyn1, dyn2, x0::AbstractVector, y0::AbstractVector,
                          time; return_solution::Bool=false, log::Bool=false)
    if log
        println("running sufficient check")
    end

    # set up problem
    h, n = check_sufficient_ode_function(dyn1, dyn2)

    z0 = [x0; y0; (x0-y0)]

    problem = DifferentialEquations.ODEProblem(h, z0, time)

    ### solve problem

    sol = DifferentialEquations.solve(problem)

    ### optimize distance

    opt_all = -Inf
    for i in (2*n+1):(3*n)
        F⁺ = (t) -> sol(t, idxs=i)
        F⁻ = (t) -> -sol(t, idxs=i)

        opt⁺ = optimize(F⁺, time[1], time[2])
        opt⁻ = optimize(F⁻, time[1], time[2])
        opt = max(abs(opt⁺.minimum), abs(opt⁻.minimum))

        opt_all = max(opt_all, opt)
    end

    ### plot solution

    if return_solution
        return opt_all, sol
    else
        return opt_all
    end
end

function check_sufficient_points(dyn1, dyn2, x0::AbstractVector, points, time,
                                 ε::Number; log::Bool=false)
    if log
        println("running sufficient check for $(length(points)) points")
    end

    points_sat = Vector{Vector{Float64}}()
    points_unsat = Vector{Vector{Float64}}()
    for p in points
        max_diff = check_sufficient(dyn1, dyn2, x0, p, time)
        if max_diff <= ε
            push!(points_sat, p)
        else
            push!(points_unsat, p)
        end
    end
    return points_sat, points_unsat
end
