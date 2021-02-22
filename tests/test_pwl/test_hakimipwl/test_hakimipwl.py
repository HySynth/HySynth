import json

import pytest
import networkx as nx
import matplotlib.pyplot as plt

from hysynth.pwl.hakimi_pwl import hakimi_algorithm as hpwl

PLOTTING_ON = False  # change this if you want to toggle plotting


@pytest.fixture()
def example_polyline():
    poly_list_y = [2, 4, 3, 6, 8, 6, 11, 6, 13, 11, 15,
                   14, 17, 16, 14, 15, 12, 13, 10, 9, 7,
                   8, 6, 7, 5, 7, 5, 6, 4, 6, 7, 5, 5, 7, 5, 6, 4, 6, 7, 5]

    x = list(range(1, len(poly_list_y) + 1))

    return list(zip(x, poly_list_y))


def test_find_pwl_e5(example_polyline):
    g = hpwl.create_approximation_graph(timeseries=example_polyline, epsilon=5)

    paths = list(nx.all_shortest_paths(g, source=example_polyline[0], target=example_polyline[-1]))

    if PLOTTING_ON:
        orig_x, orig_y = zip(*example_polyline)
        for path in paths:

            # deconstruct path
            xp, yp = zip(*path)
            fig, (ax1, ax2) = plt.subplots(nrows=2)

            ax1.scatter(orig_x, orig_y)

            ax2.scatter(orig_x, [el - 5 for el in orig_y])
            ax2.scatter(orig_x, [el + 5 for el in orig_y])
            ax2.plot(xp, yp, "o-")

            ax1.set_ylim([0, 20])
            ax2.set_ylim([0, 20])

            plt.show()

    assert [(1, 2), (12, 14), (40, 5)] == paths[0]

    assert True


def test_find_pwl_e4(example_polyline):
    g = hpwl.create_approximation_graph(timeseries=example_polyline, epsilon=4)

    paths = list(nx.all_shortest_paths(g, source=example_polyline[0], target=example_polyline[-1]))

    assert [(1, 2), (12, 14), (19, 10), (40, 5)] == paths[0]
    assert [(1, 2), (14, 16), (19, 10), (40, 5)] == paths[1]
    assert [(1, 2), (12, 14), (20, 9), (40, 5)] == paths[2]
    assert [(1, 2), (14, 16), (20, 9), (40, 5)] == paths[3]
    assert [(1, 2), (12, 14), (22, 8), (40, 5)] == paths[4]
    assert [(1, 2), (14, 16), (22, 8), (40, 5)] == paths[5]
    assert [(1, 2), (12, 14), (23, 6), (40, 5)] == paths[6]
    assert [(1, 2), (14, 16), (23, 6), (40, 5)] == paths[7]
    assert [(1, 2), (12, 14), (24, 7), (40, 5)] == paths[8]
    assert [(1, 2), (14, 16), (24, 7), (40, 5)] == paths[9]
    assert [(1, 2), (12, 14), (25, 5), (40, 5)] == paths[10]
    assert [(1, 2), (14, 16), (25, 5), (40, 5)] == paths[11]
    assert [(1, 2), (12, 14), (26, 7), (40, 5)] == paths[12]
    assert [(1, 2), (14, 16), (26, 7), (40, 5)] == paths[13]
    assert [(1, 2), (12, 14), (27, 5), (40, 5)] == paths[14]
    assert [(1, 2), (14, 16), (27, 5), (40, 5)] == paths[15]
    assert [(1, 2), (12, 14), (28, 6), (40, 5)] == paths[16]
    assert [(1, 2), (12, 14), (29, 4), (40, 5)] == paths[17]
    assert [(1, 2), (14, 16), (29, 4), (40, 5)] == paths[18]
    assert [(1, 2), (12, 14), (30, 6), (40, 5)] == paths[19]
    assert [(1, 2), (12, 14), (32, 5), (40, 5)] == paths[20]
    assert [(1, 2), (12, 14), (33, 5), (40, 5)] == paths[21]
    assert [(1, 2), (12, 14), (35, 5), (40, 5)] == paths[22]
    assert [(1, 2), (12, 14), (37, 4), (40, 5)] == paths[23]
    assert [(1, 2), (14, 16), (21, 7), (40, 5)] == paths[24]


@pytest.fixture()
def float_ts():
    """ an example that failed with epsilon 0.05 """
    return [(0.0, 5.823053052136395), (0.5, 6.323053052136395), (1.0, 6.334516913532777),
                    (1.5, 5.834516913532777), (2.0, 5.334516913532777), (2.5, 4.834516913532777),
                    (3.0, 4.334516913532777), (3.5, 3.8345169135327772), (4.0, 3.3345169135327777),
                    (4.5, 2.8345169135327777), (5.0, 3.147526055243493), (5.5, 3.647526055243493),
                    (6.0, 4.1475260552434925), (6.5, 4.6475260552434925), (7.0, 5.1475260552434925),
                    (7.5, 5.6475260552434925), (8.0, 6.1475260552434925), (8.5, 6.326952607388797),
                    (9.0, 5.826952607388797), (9.5, 5.326952607388797), (10.0, 4.8269526073887965),
                    (10.5, 4.3269526073887965), (11.0, 3.826952607388796), (11.5, 3.326952607388796),
                    (12.0, 2.8269526073887956), (12.5, 2.717869362228749), (13.0, 3.2178693622287486),
                    (13.5, 3.7178693622287486), (14.0, 4.217869362228749), (14.5, 4.717869362228748),
                    (15.0, 5.217869362228748), (15.5, 5.717869362228747), (16.0, 6.115562843265554),
                    (16.5, 5.615562843265553), (17.0, 5.115562843265551), (17.5, 4.61556284326555),
                    (18.0, 4.1155628432655496), (18.5, 3.615562843265548), (19.0, 3.1155628432655473),
                    (19.5, 2.615562843265546), (20.0, 2.863494723280435), (20.5, 3.3634947232804353),
                    (21.0, 3.8634947232804357), (21.5, 4.363494723280436), (22.0, 4.863494723280437),
                    (22.5, 5.363494723280437), (23.0, 5.8634947232804375), (23.5, 6.04650271811917),
                    (24.0, 5.54650271811917), (24.5, 5.04650271811917), (25.0, 4.54650271811917),
                    (25.5, 4.046502718119171), (26.0, 3.5465027181191706), (26.5, 3.0465027181191706),
                    (27.0, 2.546502718119171), (27.5, 2.0465027181191715)]


def test_find_pwl_float_issues(float_ts):

    approx_grap = hpwl.create_approximation_graph(timeseries=float_ts, epsilon=0.05)

    shortest_path_gen = nx.all_shortest_paths(approx_grap, float_ts[0], float_ts[-1])

    # this avoids generating all paths, since we take just the first one (saves memory and time)
    first_pwl = next(shortest_path_gen)

    assert isinstance(first_pwl, list)
    assert len(first_pwl) == 16
