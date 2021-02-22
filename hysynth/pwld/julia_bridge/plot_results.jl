using Plots, Polyhedra
using LazySets: center, HalfSpace

include("simplify_set.jl")
include("analyze_sequence.jl")
include("sample.jl")

function create_plot(; layout=1)
    return plot(aspect_ratio=1, layout=layout)
end

function plot_results(x0::AbstractVector, ε::Number, P_ua::LazySet,
                      P_oa::LazySet)
    P_full = □(x0, ε)
    return plot_results(P_full, P_ua, P_oa)
end

function plot_results(P_full::LazySet, P_ua::LazySet, P_oa::LazySet)
    p = create_plot()
    plot!(p, P_full, color=:red)
    plot!(p, P_oa, color=:yellow)
    plot!(p, simplify_overapprox(P_oa), opacity=0.2, color=:yellow)
    plot!(p, P_ua, color=:green)
    plot!(p, simplify_underapprox(P_ua), opacity=0.2, color=:green)
    return p
end

function plot_results(ε::Number, P_uas::AbstractVector, P_oas::AbstractVector,
                      xs::AbstractVector)
    p = create_plot()
    m = length(xs)
    p = plot_results(xs[2], ε, P_uas[1], P_oas[1])
    plot!(p, tickfontsize=20)
    plots = [p]
    p = plot(plots...)
    return p
end

function plot_results(ε::Number, P_uas::AbstractVector, P_oas::AbstractVector,
                      xs::AbstractVector, samples_sat_list::AbstractVector,
                      samples_unsat_list::AbstractVector)
    p = create_plot()
    plot!(p, xticks=[round(xs[1][1]; digits=2)],
             yticks=[round(xs[1][2]; digits=2)])
    plot!(p, □(xs[1], ε), color=:yellow)
    plot!(p, □(xs[1], ε), color=:green)
    plots = [p]
    m = length(xs)
    for j in 2:m
        p = plot_results(xs[j], ε, P_uas[j-1], P_oas[j-1])
        plot!(p, xticks=[round(xs[j][1]; digits=2)],
                 yticks=[round(xs[j][2]; digits=2)])
        push!(plots, p)
    end
    for (samples_sat, samples_unsat) in zip(samples_sat_list,
                                            samples_unsat_list)
        p = plot_results(xs[m], ε, P_uas[m-1], P_oas[m-1])
        plot!(p, xticks=[round(xs[end][1]; digits=2)],
                 yticks=[round(xs[end][2]; digits=2)])
        for (samples, color) in [(samples_sat, :green), (samples_unsat, :red)]
            x = [s[1] for s in samples]
            y = [s[2] for s in samples]
            plot!(p, x, y, seriestype=:scatter, color=color, label=nothing)
        end
        push!(plots, p)
    end
    p = plot(plots...)
    return p
end

function analyze_sequence_example(α, npieces; log::Bool=false)
    A = [0.0 1.0    ; -1.0 0.0]
    B = [0.0 1.0 - α; -1.0 0.0]

    As = [A for i in 1:npieces]
    Bs = [B for i in 1:npieces]
    δ = 4*π / npieces
    times = [i * δ for i in 1:npieces]

    x0 = [1.0, 1.0]
    ε = 0.1
    m = 10
    ζ = ε / 100

    answer, definite_answer, P_uas, P_oas, xs =
        analyze_sequence(As, Bs, times, x0, ε, m, ζ; log=log, return_sets=true)

    if npieces == 1
        P_uas = [P_uas[1]]
        P_oas = [P_oas[1]]
        samples_sat = samples_unsat = []
        p = plot_results(ε, P_uas, P_oas, xs)
    else
        nsamples = 1000
        samples_sat, samples_unsat = sample_points(As, Bs, xs, P_oas[end],
                                                   times, ε, nsamples; log=log)
        p = plot_results(ε, P_uas, P_oas, xs, [samples_sat], [samples_unsat])
    end

    return p
end

p = analyze_sequence_example(0.01, 1)
savefig("membership_different_1.pdf")

p = analyze_sequence_example(0.01, 23)
savefig("membership_different_23.pdf")

p = analyze_sequence_example(0.0, 1)
savefig("membership_same_1.pdf")

p = analyze_sequence_example(0.0, 23)
savefig("membership_same_23.pdf")
