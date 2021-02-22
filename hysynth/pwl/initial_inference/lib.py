# standard libraries

# external libraries
import ppl
import numpy as np

# internal libraries
from hysynth.pwl.library import float2int


def get_slopes(p1, p2):
    delta_time = p2[0] - p1[0]
    if delta_time <= 0:
        raise ValueError("Backward slopes don't make sense in this context!")

    result = []
    for i in range(1, len(p1)):
        try:
            result.append((p2[i] - p1[i]) / delta_time)

        except ZeroDivisionError as e:
            raise ValueError("Infinite slopes don't make sense in this context!") from e

    return result


def construct_flow_from_pwl(pwl_pieces_list):
    slopes_list = [get_slopes(piece_p1, piece_p2) for piece_p1, piece_p2 in pwl_pieces_list]
    average_slopes = []
    dim = len(slopes_list[0])
    for i in range(dim):
        entries_in_dim_i = [piece[i] for piece in slopes_list]
        average_slopes.append(np.mean(entries_in_dim_i))
    return average_slopes


def bloat_point(point, epsilon):
    dim = len(point)
    polyhedron = ppl.NNC_Polyhedron(dim, "universe")
    for i in range(1, dim):
        low = point[i] - epsilon
        high = point[i] + epsilon
        lower_int_conv = float2int([-1., low])
        upper_int_conv = float2int([1., -high])
        x = ppl.Variable(i)
        polyhedron.add_constraint(upper_int_conv[0] * x + upper_int_conv[1] <= 0)
        polyhedron.add_constraint(lower_int_conv[0] * x + lower_int_conv[1] <= 0)
    return polyhedron


def construct_delta_hull_pwl(points_list, epsilon):
    """
    Bloat a convex hull of points.
    Instead we compute the convex hull of the bloated points.
    Note that we do not need to project out time because the construction already keeps that dimension unconstrained.
    :param points_list: list of points
    :param epsilon: epsilon value for bloating
    :return: the bloated convex hull of the list of points
    """
    dim = len(points_list[0])
    polyhedron = ppl.NNC_Polyhedron(dim, "empty")
    for point in points_list:
        bloated_point = bloat_point(point, epsilon)
        polyhedron.poly_hull_assign(bloated_point)
    return polyhedron


def construct_invariant_polyhedral_pwl(segments_list, delta_diff):
    flattened_seg_list = list(sum(segments_list, ()))
    return construct_delta_hull_pwl(flattened_seg_list, delta_diff)


def construct_guard_polyhedral_pwl(change_points_list, delta_diff):
    return construct_delta_hull_pwl(change_points_list, delta_diff)


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")  # pragma: nocover
