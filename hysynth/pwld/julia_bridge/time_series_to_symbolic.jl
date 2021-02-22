function use_linear_search(time_series)
    return length(time_series) < 15
end

function univariate_search_bounds(p0)
    return p0[1] - 100.0, p0[1] + 100.0
end

# create diagonal matrix given x0, t, x1 s.t. x1 = e^{At}*x0 (if possible)
function guess_dyn_linear(time_series, x0)
    n = length(time_series[1]) - 1
    t_x1 = time_series[end]
    t = t_x1[1] - time_series[1][1]
    diag = Vector{Float64}(undef, n)
    for i in 1:n
        if iszero(x0[i]) || t_x1[i+1] / x0[i] <= 1e-5
            diag[i] = 0.0  # not solvable
        else
            @assert t > 0.0
            diag[i] = log(t_x1[i+1] / x0[i]) / t
        end
    end
    A = Diagonal{Float64}(diag)
    return A
end

# use constant dynamics
function guess_dyn(time_series, x0)
    n = length(time_series[1]) - 1
    t_x1 = time_series[end]
    t = t_x1[1] - time_series[1][1]
    A = zeros(n, n)
    b = [(t_x1[i+1] - x0[i]) / t for i in 1:n]
    return AffDyn(A, b)
end

function guess_x0(time_series)
    x0 = collect(time_series[1][2:end])
    return x0
end

# convert parameter array to symbolic representation
function parametric_to_symbolic(p, n; first::Bool=false, linear::Bool=false)
    A = Matrix{Float64}(undef, n, n)
    k = 0
    for j in 1:n
        for i in 1:n
            A[i, j] = p[k + i]
        end
        k += n
    end

    if linear
        dyn = A
    else
        b = p[(n*n+1):(n*(n+1))]
        dyn = AffDyn(A, b)
    end

    if first
        x0 = p[(end-n+1):end]
        return dyn, x0
    else
        return dyn
    end
end

# solve ODE problem in continuous time
function solve_ode_continuous(dyn, x0, time)
    f(u, p, t) = dyn.A * u + dyn.b
    problem = DifferentialEquations.ODEProblem(f, x0, time)
    sol = DifferentialEquations.solve(problem)
    return sol
end

# solve ODE problem at discrete points in time
function solve_ode_discrete(dyn, x0, time)
    return (t) -> successor(dyn, t, x0)
end

# distance between ODE solution and time series
function distance(dyn, x0, time_series)
    d = -Inf
    t0 = time_series[1][1]
    for t_p_ts in time_series
        t = t_p_ts[1] - t0
        p_ts = t_p_ts[2:end]
        p_ode = successor(dyn, t, x0)
        if p_ode == nothing
            return Inf  # exact solution failed
        end
        d_raw = map(-, p_ts, p_ode)
        d_new = norm(d_raw, Inf)  # infinity norm of the distance
        d = max(d, d_new)
    end
    return d
end

# distance between parametric representation and time series
function parametric_problem(p, time_series, n, x0; linear::Bool=false)
    first = x0 == nothing

    # convert to symbolic representation
    result = parametric_to_symbolic(p, n; first=first, linear=linear)
    if first
        dyn, x0 = result
    else
        dyn = result
    end

    # compute distance between ODE solution and time series
    d = distance(dyn, x0, time_series)

    return d
end

# convert symbolic representation to parameter array
function symbolic_to_parametric(dyn, n, x0=nothing; linear::Bool=linear)
    first = x0 != nothing
    b_factor = linear ? 0 : 1
    A = linear ? dyn : dyn.A

    p = Vector{Float64}(undef,
                        first ? n * (n + 1 + b_factor) : n * (n + b_factor))
    k = 0
    for j in 1:n
        for i in 1:n
            p[k + i] = A[i, j]
        end
        k += n
    end
    if !linear
        p[(n*n+1):(n*(n+1))] = dyn.b
    end
    if first
        p[(end-n+1):end] = x0
    end
    return p
end

function time_series_to_symbolic_one_piece(time_series, dyn_init, x0_init;
                                           first::Bool=false,
                                           linear::Bool=false)
    # problem dimension
    n = length(time_series[1]) - 1

    # distance function to optimize
    x0_init_use = first ? nothing : x0_init
    dist = (p) -> parametric_problem(p, time_series, n, x0_init_use;
                                     linear=linear)

    # convert initial guess to parametric representation
    if first
        p0 = symbolic_to_parametric(dyn_init, n, x0_init; linear=linear)
    else
        p0 = symbolic_to_parametric(dyn_init, n; linear=linear)
    end

    # optimize
    if length(p0) == 1
        bounds = univariate_search_bounds(p0)
        sol = optimize(dist, bounds[1], bounds[2])
    else
        sol = optimize(dist, p0)
    end
    p = sol.minimizer
    min_d = sol.minimum

    result = parametric_to_symbolic(p, n; first=first, linear=linear)
    if first
        dyn, x0 = result
        return dyn, x0, min_d
    else
        dyn = result
        return dyn, min_d
    end
end

function time_series_to_symbolic_longest_piece(time_series, ε, dyn_init,
                                               x0_init;
                                               linear_search::Bool=true,
                                               first::Bool=false)
    guess_dyn_first = dyn_init == nothing
    solution_found = false
    i = length(time_series)
    binary_search_range = [1, i+1]  # range [l, u] where l works and u does not
    dyn_best = nothing
    x0_best = nothing
    while i > 1
        time_series_shortened = time_series[1:i]

        for linear in [true, false]
            if length(time_series_shortened) == 2 && linear
                # skipping linear fit
                continue
            end

            if guess_dyn_first
                if linear
                    dyn_init_use = guess_dyn_linear(time_series_shortened,
                                                    x0_init)
                else
                    dyn_init_use = guess_dyn(time_series_shortened, x0_init)
                end
            else
                if linear
                    dyn_init_use = dyn_init.A
                else
                    dyn_init_use = dyn_init
                end
            end

            result = time_series_to_symbolic_one_piece(time_series_shortened,
                                                       dyn_init_use, x0_init;
                                                       first=first,
                                                       linear=linear)
            if first
                dyn, x0, min_d = result
            else
                dyn, min_d = result
            end
            if min_d <= ε
                if linear
                    @assert dyn isa AbstractMatrix
                    n = length(time_series[1]) - 1
                    dyn = AffDyn(dyn, zeros(n))
                else
                    @assert dyn isa AffDyn
                end
                dyn_best = dyn
                if first
                    x0_best = x0
                end
                solution_found = true
                break
            end
        end
        guess_dyn_first = true

        if linear_search
            # linear search
            if !solution_found
                i -= 1
                solution_found = false
                continue
            end
        else
            # binary search, rounding up
            if solution_found
                binary_search_range[1] = i
            else
                binary_search_range[2] = i
            end
            if binary_search_range[1] < binary_search_range[2] - 1
                i = div(binary_search_range[1] + binary_search_range[2] + 1, 2)
                solution_found = false
                continue
            end
        end

        # found the largest solution
        if !linear_search
            i = binary_search_range[1]
        end
        @assert dyn_best != nothing
        if first
            @assert x0_best != nothing
            return dyn_best, x0_best, i
        else
            return dyn_best, i
        end
    end
    @assert false "it should always be possible to fit a function to two points"
end

function time_series_to_symbolic(time_series, ε, dyn_init, x0_init;
                                 linear_search::Bool=use_linear_search(time_series),
                                 log::Bool=false)
    @assert iszero(time_series[1][1]) "the time series should start with t = 0 but started with " *
        time_series[1][1]

    if x0_init == nothing
        x0_init = guess_x0(time_series)
    end

    dyn, x0, l = time_series_to_symbolic_longest_piece(time_series, ε, dyn_init,
        x0_init; linear_search=linear_search, first=true)
    t = time_series[l][1]
    x1 = successor(dyn, t, x0)
    dyns = [dyn]
    times = [t]
    indices = [l]
    while l < length(time_series)
        time_series_shortened = time_series[l:end]
        dyn, Δl = time_series_to_symbolic_longest_piece(time_series_shortened,
            ε, nothing, x1; linear_search=linear_search, first=false)
        l_new = l + Δl - 1
        t = time_series[l_new][1] - time_series[l][1]
        x1 = successor(dyn, t, x1)
        l = l_new
        push!(dyns, dyn)
        push!(times, time_series[l_new][1])
        push!(indices, l)
    end
    if log
        println("found a function with $(length(dyns)) pieces")
    end
    return dyns, x0, times, indices
end
