import subprocess as sp


def parse_number(string):
    if string[0] == '(':
        # negative number
        assert string[1] == '-' and string[len(string) - 1] == ')'
        string = string[2:len(string) - 1]
        assert string[len(string) - 2:] == '.0'
        string = string[0:len(string) - 2]
        num = -int(string)
    else:
        # nonnegative number
        assert string[len(string) - 2:] == '.0'
        string = string[0:len(string) - 2]
        num = int(string)
    return num


def parse_fraction(line, second_line=None):
    space_index = line.find(' ')
    first_number = parse_number(line[0:space_index])
    if second_line is None:
        # the whole fraction is given in one line
        line = line[space_index + 1:]
        paren_index = line.find(')')
        second_number = parse_number(line[0:paren_index])
    else:
        # the denominator is given in the next line
        assert space_index == -1
        paren_index = second_line.find(')')
        second_number = parse_number(second_line[0:paren_index])
    return first_number / second_number


def line_to_valuation(line, second_line=None):
    line = line[2:]
    end_var_name = line.find(' ')
    var = line[0:end_var_name]
    line = line[end_var_name + 1:]
    if line[0] == '(':
        # value is a fraction or negative number
        if line[1] == '/':
            # value is a positive fraction
            assert line.find('-') == -1
            line = line[3:]
            val = parse_fraction(line, second_line)
        else:
            assert line[1] == '-'
            if line[4] == '/':
                # value is a negative fraction
                line = line[6:]
                val = - parse_fraction(line, second_line)
            else:
                # value is a negative number
                paren_index = line.find(')')
                val = parse_number(line[0:paren_index + 1])
    else:
        # value is a positive number
        paren_index = line.find(')')
        val = parse_number(line[0:paren_index])
    return var, val


def run_smt_solver(smt_string):
    """Send a satisfiability query to an SMT solver"""

    folder = '../'

    input_file = folder + 'problem.smt2'
    f = open(input_file, 'w')
    f.write(smt_string)
    f.close()

    output_file = folder + 'solution.smt2'
    sp.call(['sh', folder + 'smt.sh', input_file, output_file])

    sol = open(output_file, 'r')
    output_string = sol.readline()
    output_string = output_string.strip()

    valuation = []
    if output_string == 'sat':
        result = True
        cached_line = None
        for line in sol:
            if cached_line is None:
                if line[-2] == ')':
                    # whole valuation is given in one line
                    valuation.append(line_to_valuation(line=line))
                else:
                    # valuation is given in two lines; cache this line and continue in the next iteration
                    cached_line = line
            else:
                # pass a two-line valuation
                valuation.append(line_to_valuation(line=cached_line, second_line=line))
                cached_line = None
        sol.close()
    elif output_string == 'unsat':
        result = False
        sol.close()
    else:
        sol.close()
        raise Exception('error: unexpected SMT solver output: {0}'.format(output_string))

    return result, valuation
