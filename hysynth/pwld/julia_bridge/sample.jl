using Distributions
using LazySets: sample, dim

# TODO generalize to affine dynamics

function sample_points_backward(As::AbstractVector, Bs::AbstractVector,
                                x_last::AbstractVector, P_last::LazySet,
                                times::AbstractVector, ε::Number,
                                nsamples::Integer;
                                log::Bool=false)
    samples_sat = Vector{Vector{Float64}}()
    samples_unsat = Vector{Vector{Float64}}()
    box = box_approximation(P_last)
    if isflat(box)
        samples = [center(box)]
    else
        samples = sample(P_last, nsamples)
    end
    l = length(As)
    if log
        println("sampling $(length(samples)) points")
    end
    for y0 in samples
        samples = samples_sat
        x = x_last
        y = y0
        for k in l:-1:1
            A = -As[k]
            B = -Bs[k]
            T = times[k]
            T_prev = (k == 1) ? 0 : times[k-1]
            time = (T_prev, T)
            max_diff = check_sufficient(A, B, x, y, time)
            if max_diff > ε
                samples = samples_unsat
                break
            end
            T = time[2] - time[1]
            x = exp(A * T) * x
            y = exp(B * T) * y
        end
        push!(samples, y0)
    end
    if log
        println("$(length(samples_sat)) sat samples and " *
                "$(length(samples_unsat)) unsat samples")
    end
    return samples_sat, samples_unsat
end

function sample_points(As::AbstractVector, Bs::AbstractVector,
                       xs::AbstractVector, P_last::LazySet,
                       times::AbstractVector, ε::Number,
                       nsamples::Integer;
                       log::Bool=false)
    return sample_points_backward(As, Bs, xs[end], P_last, times, ε, nsamples;
                                  log=log)
end

function sample_points_init(As::AbstractVector, Bs::AbstractVector,
                            x0::AbstractVector, P_last::LazySet,
                            times::AbstractVector, ε::Number,
                            nsamples::Integer;
                            log::Bool=false)
    x_last = x0
    T = 0.0
    for k in 1:length(As)
        A = As[k]
        T = times[k] - T
        x_last = exp(A * T) * x_last
    end
    return sample_points_backward(As, Bs, x_last, P_last, times, ε, nsamples;
                                  log=log)
end
