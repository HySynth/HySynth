def positive_number_to_smt(number):
    """
    Print a floating-point number in decimal notation (i.e., prevent scientific notation).
    This code is taken from https://stackoverflow.com/a/45604186.
    :param number: floating-point number
    :return: string in decimal notation
    """
    number_as_two_strings = str(number).split('e')
    if len(number_as_two_strings) == 1:
        # no scientific notation needed
        return number_as_two_strings[0]
    base = float(number_as_two_strings[0])
    exponent = int(number_as_two_strings[1])
    result = ''
    if int(exponent) > 0:
        result += str(base).replace('.', '')
        result += ''.join(['0' for _ in range(0, abs(exponent - len(str(base).split('.')[1])))])
    elif int(exponent) < 0:
        result += '0.'
        result += ''.join(['0' for _ in range(0, abs(exponent) - 1)])
        result += str(base).replace('.', '')
    return result


def number_to_smt(x):
    if x >= 0:
        return '{0}'.format(positive_number_to_smt(x))
    else:
        return '(- {0})'.format(positive_number_to_smt(abs(x)))


def declare_const(name):
    return '(declare-const {0} Real)\n'.format(name)


def constraint_switch_definition(i, j, t, fi):
    return '(assert (= x_f{2}_p{1}_d{0} (+ x_f{2}_p{3}_d{0} (* {4} b_f{2}_p{1}_d{0}))))\n'.format(i, j, fi, j-1, t)


def constraint_switch_epsilon_close(i, j, old_value, epsilon, fi):
    return '(assert (<= {3} x_f{2}_p{1}_d{0} {4}))\n'.format(
        i, j, fi, number_to_smt(old_value - epsilon), number_to_smt(old_value + epsilon))


def constraint_slope_choice(j, dimension, number_slopes, existing_slopes, fi):
    string = '(assert (or '

    for k in range(1, number_slopes + 1):
        if k > 1:
            string += '            '
        string += '(and '
        for i in range(1, dimension + 1):
            string += '(= b_f{2}_p{1}_d{0} a_k{3}_d{0}) '.format(i, j, fi, k)
        string += ')\n'

    print_spaces = number_slopes > 0
    for slope in existing_slopes:
        if print_spaces:
            string += '            '
        else:
            print_spaces = True
        string += '(and '
        for i in range(1, dimension + 1):
            string += '(= b_f{2}_p{1}_d{0} {3}) '.format(i, j, fi, number_to_smt(slope[i - 1]))
        string += ')\n'

    string += '))\n'
    return string


def pwl_function_to_smt(functions, epsilon, number_slopes, existing_slopes=[]):
    """
    Create an SMT-LIB string that encodes the synthesis of a PWL function that
    is 'epsilon'-close to 'f' and has at most 'number_slopes' many slopes (in
    addition to those in 'existing_slopes')

    :param functions: list of PWL functions
    :param epsilon: error value
    :param number_slopes: maximum number of slopes
    :param existing_slopes: (optional) list of existing slopes (not included in the 'number_slopes' count)
    :return: an SMT-LIB compliant string
    """
    string = ''

    # preliminaries
    string += '(set-option :print-success false)\n'
    string += '(set-option :produce-models true)\n'
    string += '(set-logic QF_LRA)\n'
    string += '\n'

    dimension = len(functions[0][0]) - 1

    # declare variables
    for i in range(1, dimension + 1):
        # declare target slopes
        for j in range(1, number_slopes + 1):
            string += declare_const('a_k{1}_d{0}'.format(i, j))

    fi = 0
    for f in functions:
        m = len(f) - 1
        fi += 1

        # declare new switching points
        for j in range(m + 1):
            for i in range(1, dimension + 1):
                string += declare_const('x_f{2}_p{1}_d{0}'.format(i, j, fi))

        # declare new switching points
        for j in range(1, m + 1):
            for i in range(1, dimension + 1):
                string += declare_const('b_f{2}_p{1}_d{0}'.format(i, j, fi))

    string += '\n'

    fi = 0
    for f in functions:
        m = len(f) - 1
        fi += 1

        # value constraints for new switching points
        t0 = f[0][0]
        for j in range(1, m + 1):
            t1 = f[j][0]
            t = t1 - t0
            for i in range(1, dimension + 1):
                string += constraint_switch_definition(i=i, j=j, t=t, fi=fi)
            t0 = t1

        # epsilon constraints for each switching point
        for j in range(0, m + 1):
            old_point = f[j]
            for i in range(1, dimension + 1):
                string += constraint_switch_epsilon_close(i=i, j=j, old_value=old_point[i], epsilon=epsilon, fi=fi)

        # slope-choice constraints
        for j in range(1, m + 1):
            string += constraint_slope_choice(j=j, dimension=dimension, number_slopes=number_slopes,
                                              existing_slopes=existing_slopes, fi=fi)

    # check-sat command
    string += '(check-sat)\n'

    # get values of interesting variables (slopes and slope orders)
    string += '(get-value ('
    for j in range(1, number_slopes + 1):
        for i in range(1, dimension + 1):
            string += 'a_k{1}_d{0} '.format(i, j)
    fi = 0
    for f in functions:
        m = len(f) - 1
        fi += 1
        for j in range(1, m + 1):
            for i in range(1, dimension + 1):
                string += 'b_f{2}_p{1}_d{0} '.format(i, j, fi)
    fi = 0
    for f in functions:
        m = len(f) - 1
        fi += 1
        for j in range(0, m + 1):
            for i in range(1, dimension + 1):
                string += 'x_f{2}_p{1}_d{0} '.format(i, j, fi)
    string += '))\n'

    return string
