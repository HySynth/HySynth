import ppl

import hysynth.pwl.ndim_library as nlib


def test_unit_cube_xz_displacement():

    x = ppl.Variable(0)
    y = ppl.Variable(1)
    z = ppl.Variable(2)

    initpoly = ppl.NNC_Polyhedron(3,'universe')
    initpoly.add_constraint(x >= 0)
    initpoly.add_constraint(x <= 1)
    initpoly.add_constraint(y >= 0)
    initpoly.add_constraint(y <= 1)
    initpoly.add_constraint(z >= 0)
    initpoly.add_constraint(z <= 1)

    finalpoly = ppl.NNC_Polyhedron(3, 'universe')
    finalpoly.add_constraint(x >= 3)
    finalpoly.add_constraint(x <= 6)
    finalpoly.add_constraint(y >= -2)
    finalpoly.add_constraint(y <= 2)
    finalpoly.add_constraint(z >= 3)
    finalpoly.add_constraint(z <= 6)

    slope = [0,1]

    reachpoly = ppl.NNC_Polyhedron(3,'universe')
    reachpoly.add_constraint(x >= 3)
    reachpoly.add_constraint(x <= 6)
    reachpoly.add_constraint(y >= 0)
    reachpoly.add_constraint(y <= 1)
    reachpoly.add_constraint(z >= 3)
    reachpoly.add_constraint(z <= 6)
    reachpoly.add_constraint(x - z <= 1)
    reachpoly.add_constraint(x - z >= -1)


    result = nlib.npost(initpoly, finalpoly, slope)

    # print('result constraints =', result.minimized_constraints())
    # print('reachpoly constraints =', reachpoly.minimized_constraints())
    # print()
    # print('result generators =', result.generators())
    # print('reachpoly generators =', reachpoly.generators())

    for result_generator, reachpoly_generator in zip(result.generators(), reachpoly.generators()):
        assert result_generator.coefficients() == reachpoly_generator.coefficients()


# def test_unit_cube_diagonal_displacement():
#
#     x = ppl.Variable(0)
#     y = ppl.Variable(1)
#     z = ppl.Variable(2)
#
#     initpoly = ppl.NNC_Polyhedron(3,'universe')
#     initpoly.add_constraint(x >= 0)
#     initpoly.add_constraint(x <= 1)
#     initpoly.add_constraint(y >= 0)
#     initpoly.add_constraint(y <= 1)
#     initpoly.add_constraint(z >= 0)
#     initpoly.add_constraint(z <= 1)
#
#     finalpoly = ppl.NNC_Polyhedron(3, 'universe')
#     finalpoly.add_constraint(x >= 3)
#     finalpoly.add_constraint(x <= 4)
#     finalpoly.add_constraint(z >= 3)
#     finalpoly.add_constraint(z <= 4)
#
#     slope = [1,1]
#
#     reachpoly = ppl.NNC_Polyhedron(3,'universe')
#     reachpoly.add_constraint(x >= 3)
#     reachpoly.add_constraint(x <= 4)
#     reachpoly.add_constraint(z >= 3)
#     reachpoly.add_constraint(z <= 4)
#     reachpoly.add_constraint(y - x <= 1)
#     reachpoly.add_constraint(y - x >= -1)
#
#
#     result = nlib.npost(initpoly, finalpoly, slope)
#
#     print('result constraints =', result.minimized_constraints())
#     print('reachpoly constraints =', reachpoly.minimized_constraints())
#     print()
#     print('result generators =', result.generators())
#     print('reachpoly generators =', reachpoly.generators())
#
#     for result_generator, reachpoly_generator in zip(result.generators(), reachpoly.generators()):
#         assert result_generator.coefficients() == reachpoly_generator.coefficients()