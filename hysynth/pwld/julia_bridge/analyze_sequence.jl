include("analyze_piece.jl")
include("simplify_set.jl")

function analyze_sequence(dyns1::AbstractVector, dyns2::AbstractVector,
                          times::AbstractVector, x0::AbstractVector, ε::Number,
                          m::Integer, ζ::Number;
                          log::Bool=false, return_sets::Bool=false)
    time = (0.0, times[1])
    P0 = □(x0, ε)
    for simplify_underapproximation in [true, false]
        if log
            println("* piece #1")
        end
        dyn1 = dyns1[1]
        dyn2 = dyns2[1]
        P1_ua, P1_oa, _, x1 =
            analyze_piece(dyn1, dyn2, x0, P0, ε, time, m, ζ, true; log=log)
        if return_sets
            P_uas = Vector{LazySet{Float64}}()
            push!(P_uas, P1_ua)
            P_oas = Vector{LazySet{Float64}}()
            push!(P_oas, P1_oa)
            xs = [x0, x1]
        end

        if isempty(P1_ua)
            answer = false
            is_definite_answer = false
            loop_break = true
            try_again = false
            n_loop = 0
            if log
                println("underapproximation is empty => give up")
            end
        else
            answer = true
            is_definite_answer = false
            loop_break = false
            try_again = false
            n_loop = length(dyns1)
        end

        for k in 2:n_loop
            if log
                println("* piece #$k")
            end

            dyn1 = dyns1[k]
            dyn2 = dyns2[k]
            time = (times[k-1], times[k])
            x0 = x1

            # overapproximation
            P0_oa = simplify_overapprox(P1_oa)
            P1_oa = analyze_piece(dyn1, dyn2, x0, P0_oa, ε, time, m, ζ, false;
                                  log=log)

            if isempty(P1_oa)
                if log
                    println("overapproximation is empty => no solution exists")
                end
                answer = false
                is_definite_answer = true
                loop_break = true
                break
            end

            # underapproximation
            P0_ua =
                simplify_underapprox(P1_ua; ignore=!simplify_underapproximation)
            P1_ua, _, _, x1 = analyze_piece(dyn1, dyn2, x0, P0_ua, ε, time, m,
                                            ζ, true; log=log)

            if isempty(P1_ua)
                answer = false
                is_definite_answer = false
                loop_break = true
                try_again = simplify_underapproximation
                if log
                    print("underapproximation is empty")
                    if try_again
                        println(" => trying again with more precise analysis")
                    else
                        println(" => give up")
                    end
                end
                break
            end

            if return_sets
                push!(P_uas, P1_ua)
                push!(P_oas, P1_oa)
                push!(xs, x1)
            end
        end

        if !loop_break
            answer = true
            is_definite_answer = !isempty(P1_ua)
        end

        if try_again
            if log
                println("trying analysis again without simplifying underapproximation")
            end
            continue
        end

        if return_sets
            return answer, is_definite_answer, P_uas, P_oas, xs
        end
        return answer, is_definite_answer
    end
end
