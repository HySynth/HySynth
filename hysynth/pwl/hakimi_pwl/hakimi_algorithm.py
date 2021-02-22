"""
This module implements the algorithm for computing a Piecewise-Linear approximation of a time-series.

Hakimi, S. L., & Schmeichel, E. F. (1991).
Fitting polygonal functions to a set of points in the plane.
CVGIP: Graphical Models and Image Processing, 53(2), 132–136.
https://doi.org/10.1016/1049-9652(91)90056-P

"""
import numpy as np
import networkx as nx
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from hysynth.pwl.hakimi_pwl.visibility_polygon import make_bounded_polygon,\
    visibility_for_point, create_environment_for_visibility


def create_approximation_graph(timeseries, epsilon: (float, int)):
    """

    Iterate over the points
    and for each point compute the visibility polygon
    then for all the points after it compute whether they are visible from the initial point i.e.
    are in the visibility polygon
    if they are, add a directed edge to the graph from initial point to the visible one

    Parameters
    ----------
    timeseries
    epsilon

    Returns
    -------

    """

    if isinstance(timeseries, list) and all(map(lambda el: isinstance(el, tuple) and len(el) == 2, timeseries)):
        polygonal_line = timeseries  # all ok

    elif isinstance(timeseries, list) and all(map(lambda el: isinstance(el, list) and len(el) == 2, timeseries)):
        polygonal_line = [(el[0], el[1]) for el in timeseries]

    elif isinstance(timeseries, np.ndarray) and timeseries.shape[0] == 2:
        polygonal_line = [(el[0], el[1]) for el in timeseries]

    else:
        raise TypeError("Timeseries is not provided in the right format!")

    # create the bounded polygon class, which contains the bounds and functions for visibility computation
    bp = make_bounded_polygon(polygonal_line, epsilon)
    vis_env = create_environment_for_visibility(bounded_poly=bp)

    # create the directed graph and add all the datapoints as nodes
    graph = nx.DiGraph()
    graph.add_nodes_from(polygonal_line)

    # MAIN PART OF THE ALGORITHM

    # iterate over all points from first to one before last
    for idx, current_point in enumerate(bp.polyline):

        # for each point compute the visibility polygon
        visp = visibility_for_point(vis_env=vis_env, point1=current_point)
        max_x = max(visp, key=lambda x: x[0])[0]
        max_idx = max([i for i, val in enumerate(bp.polyline) if val[0] <= max_x])

        # iterate over all the points after the current point ( +1 python indexing)
        for next_point in bp.polyline[idx + 1: max_idx + 1]:

            # check if point is visible
            if is_point_in_bounds(visibility_polygon=visp, point2=next_point):

                # if it is add a directed edge
                graph.add_edge(current_point, next_point)

    return graph


def is_point_in_bounds(visibility_polygon, point2):
    point = Point(*point2)
    polygon = Polygon(visibility_polygon)
    return polygon.contains(point)


if __name__ == "__main__":
    raise RuntimeError("Do not run this module directly!")
