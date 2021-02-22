def distance_point_line_segment(point, ls_left, ls_right):
    """
    Compute the (infinity-norm) distance of a point and a line segment over time defined by its end points.
    :param point: point
    :param ls_left: left point of the line segment
    :param ls_right: right point of the line segment
    :return: distance of the line segment and the given point (in the infinity norm)
    """
    tl = ls_left[0]
    tr = ls_right[0]
    tp = point[0]
    xl = ls_left[1:]
    xr = ls_right[1:]
    xp = point[1:]
    m = [(xr[i] - xl[i]) / (tr - tl) for i in range(len(xr))]
    xt = [xl[i] + m[i] * (tp - tl) for i in range(len(xr))]  # projection of point on the line segment in time
    res = max([abs(xp[i] - xt[i]) for i in range(len(xr))])  # compute the distance in the infinity norm
    return res


def ramer_douglas_peucker(time_series, epsilon):
    """
    Compute an epsilon-close PWL approximation of time-series data using the Ramer-Douglas-Peucker algorithm.
    The code follows https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm#Pseudocode .
    :param time_series:
    :param epsilon: epsilon value
    :return: new time-series data with a subset of the original points
    """
    # find the point with the maximum distance
    max_distance = 0
    index = 0
    l0 = time_series[0]
    l1 = time_series[-1]
    for i in range(1, len(time_series) - 1):
        dist = distance_point_line_segment(time_series[i], l0, l1)
        if dist > max_distance:
            index = i
            max_distance = dist

    if max_distance > epsilon:
        # split line segment recursively
        result1 = ramer_douglas_peucker(time_series[0:index+1], epsilon)
        result2 = ramer_douglas_peucker(time_series[index:], epsilon)
        result = result1[0:-1] + result2
    else:
        # keep line segment
        result = [time_series[0], time_series[-1]]

    return result
