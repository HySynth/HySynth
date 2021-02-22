from . import pwl_function_to_smt, run_smt_solver

def minimize_slopes(functions, epsilon, existing_slopes=[]):
    if existing_slopes:
        k = -1
    else:
        k = 0
    while True:
        k += 1
        smt_string = pwl_function_to_smt(functions=functions, epsilon=epsilon, number_slopes=k,
                                         existing_slopes=existing_slopes)
        result, valuation = run_smt_solver(smt_string=smt_string)

        if result:
            break
        else:
            print("no solution of size {0}".format(k))
    return k, valuation
