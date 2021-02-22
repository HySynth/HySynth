import ppl

import hysynth.pwl.ndim_library as nlib


def test_unit_cube_xz_displacement():

    x = ppl.Variable(0)
    y = ppl.Variable(1)
    z = ppl.Variable(2)


    initpoly = ppl.NNC_Polyhedron(3,'universe')
    initpoly.add_constraint(x >= 3)
    initpoly.add_constraint(x <= 6)
    initpoly.add_constraint(y >= 0)
    initpoly.add_constraint(y <= 1)
    initpoly.add_constraint(z >= 3)
    initpoly.add_constraint(z <= 6)
    initpoly.add_constraint(x - z <= 1)
    initpoly.add_constraint(x - z >= -1)

    finalpoly = ppl.NNC_Polyhedron(3, 'universe')
    finalpoly.add_constraint(x >= -2)
    finalpoly.add_constraint(x <= 2)
    finalpoly.add_constraint(y >= -2)
    finalpoly.add_constraint(y <= 2)
    finalpoly.add_constraint(z >= -2)
    finalpoly.add_constraint(z <= 2)

    slope = [0,1]

    reachpoly = ppl.NNC_Polyhedron(3, 'universe')
    reachpoly.add_constraint(x >= 0)
    reachpoly.add_constraint(x <= 1)
    reachpoly.add_constraint(y >= 0)
    reachpoly.add_constraint(y <= 1)
    reachpoly.add_constraint(z >= 0)
    reachpoly.add_constraint(z <= 1)


    result = nlib.npost(initpoly, finalpoly, slope)

    for result_generator, reachpoly_generator in zip(result.generators(), reachpoly.generators()):
        assert result_generator.coefficients() == reachpoly_generator.coefficients()