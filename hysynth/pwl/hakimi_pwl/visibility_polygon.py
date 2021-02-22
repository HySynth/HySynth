""" This module implements the visibility polygon computation needed in the Hakimi algorithm """

from collections import namedtuple
import visilibity as vis

FLOATS_EPSILON = 1e-07


def create_environment_for_visibility(bounded_poly, offset=2):
    """ This function create the necessary environment for the computation of the visibility window """

    x_values, y_values = zip(*bounded_poly.full_bounded_poly)

    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)

    p1 = vis.Point(x_min - offset, y_max)
    p2 = vis.Point(x_max + offset, y_max)
    p3 = vis.Point(x_max + offset, y_min)
    p4 = vis.Point(x_min - offset, y_min)

    walls = vis.Polygon([p4, p3, p2, p1])

    extended_upper_bound = extend_bounds(bounded_poly.upper_bound, offset)
    extended_lower_bound = extend_bounds(bounded_poly.lower_bound, offset)

    upper_boundry = vis.Polygon([p1, p2] + [vis.Point(*current_point)
                                            for current_point in extended_upper_bound][::-1])

    lower_boundry = vis.Polygon([vis.Point(*current_point)
                                 for current_point in extended_lower_bound] + [p3, p4])

    return vis.Environment([walls, upper_boundry, lower_boundry])


def extend_bounds(bound_list, offset):
    first_el_x, first_el_y = bound_list[0]
    last_el_x, last_el_y = bound_list[-1]

    return [(first_el_x - offset, first_el_y)] + bound_list + [(last_el_x + offset, last_el_y)]


def visibility_for_point(vis_env, point1):
    """ This computes the visibility polygon for a specific point and outputs the vertices of the polygon"""

    # observer is the point
    observer = vis.Point(*point1)

    # Necessary to generate the visibility polygon
    observer.snap_to_boundary_of(vis_env, FLOATS_EPSILON)
    observer.snap_to_vertices_of(vis_env, FLOATS_EPSILON)

    # Obtain the visibility polygon of the 'observer' in the environment
    # previously define
    isovist = vis.Visibility_Polygon(observer, vis_env, FLOATS_EPSILON)

    return [(isovist[i].x(), isovist[i].y()) for i in range(isovist.n())]


BoundedPolygon = namedtuple("BoundedPolygon", ["polyline", "upper_bound", "lower_bound", "full_bounded_poly"])


def make_bounded_polygon(polyline, epsilon_bound):
    upper_bound = list(map(lambda x: (x[0], x[1] + epsilon_bound), polyline))
    lower_bound = list(map(lambda x: (x[0], x[1] - epsilon_bound), polyline))

    full_bounded_poly = [polyline[0]] + upper_bound + [polyline[-1]] + lower_bound

    return BoundedPolygon(polyline=polyline,
                          upper_bound=upper_bound,
                          lower_bound=lower_bound,
                          full_bounded_poly=full_bounded_poly)


if __name__ == "__main__":
    raise RuntimeError("Don't run this module directly!")
