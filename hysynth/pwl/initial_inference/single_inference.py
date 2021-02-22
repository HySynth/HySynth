# standard libraries
import itertools
from collections import defaultdict

# external libraries
import pandas as pd
from sklearn.cluster import MeanShift

# internal libraries
from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwl.library import check_clustering_bandwidth
from hysynth.utils.hybrid_system.library import construct_hybrid_automaton_name, construct_location_name, \
    construct_variable_names
from hysynth.pwl.initial_inference import lib as init_lib


def infer_hybrid_system_polyhedral_pwl(pwl_points_list, delta_ha, delta_fh,
                                       epsilon_meanshift=False, hybrid_system_name=None,
                                       pwl_slopes=None, only_consider_first_piece=True):
    """ This function is the initial hybrid system inference function """

    # some safety and integrity checks since this is the outer interface function
    if not isinstance(pwl_points_list, list):
        raise TypeError("The variable <pwl_points_list> must be a list!")

    check_clustering_bandwidth(epsilon_meanshift)

    if not isinstance(delta_fh, (float, int)):
        raise TypeError("The argument <delta_fh> must be numeric!")

    hybrid_system_name = construct_hybrid_automaton_name(hybrid_system_name)

    if not isinstance(hybrid_system_name, str):
        raise TypeError("The argument <hybrid_system_name> must be a string!")

    variable_names = construct_variable_names(pw_function=pwl_points_list, function_type="pwl")

    # initialize the hybrid system that we are trying to construct
    inferred_hybrid_system = HybridSystemPolyhedral(name=hybrid_system_name,
                                                    variable_names=variable_names,
                                                    delta=delta_ha)

    if only_consider_first_piece:
        # only use the first piece
        pwl_pieces_list = [tuple([pwl_points_list[0], pwl_points_list[1]])]
    else:
        # consider all pieces
        pwl_pieces_list = list(zip(pwl_points_list[:-1], pwl_points_list[1:]))

    if pwl_slopes is None:
        pwl_slopes = get_pwl_slopes(pwl_pieces_list=pwl_pieces_list)
    pwl_slopes_df = pd.DataFrame(pwl_slopes)

    if epsilon_meanshift is not False:
        # get the modes by clustering
        clustered_pwl_dict = meanshift_clustering(segment_flows_df=pwl_slopes_df,
                                                  epsilon=epsilon_meanshift)

    else:

        # if clustering is disabled each piece is its own class
        clustered_pwl_dict = defaultdict(list)
        slopes_ids_dict = defaultdict(tuple)

        for idx, row in pwl_slopes_df.iterrows():

            curr_slope = tuple(row.values)
            slope_id = slopes_ids_dict.get(curr_slope, None)

            if slope_id is None:
                slopes_ids_dict[curr_slope] = idx
                clustered_pwl_dict[idx].append(idx)

            else:
                clustered_pwl_dict[slope_id].append(idx)

    # start building the Hybrid System, starting with locations, invariants and flows
    for cluster_id, cluster_segments_ids in clustered_pwl_dict.items():

        location_name = construct_location_name(cluster_id)

        # for each cluster, make a mode/location
        inferred_hybrid_system.add_location(location_name)

        # separate out the pwl pieces belonging to this class
        cluster_pieces = [pwl_pieces_list[idx] for idx in cluster_segments_ids]

        # next construct the invariants
        invariant = init_lib.construct_invariant_polyhedral_pwl(segments_list=cluster_pieces,
                                                                delta_diff=delta_fh)

        inferred_hybrid_system.set_invariant(location_name, invariant)

        # next construct the flow

        # get the flowtube collection
        flow_slope = init_lib.construct_flow_from_pwl(pwl_pieces_list=cluster_pieces)

        inferred_hybrid_system.set_flow(location_name, flow_slope, rounding=True)

    # check all the combinations of locations CrossProduct
    for cluster1_id, cluster2_id in itertools.product(clustered_pwl_dict.keys(), repeat=2):

        # we do not allow self loops for now
        if cluster1_id == cluster2_id:
            continue

        # get all the changepoints for each of the classes

        # for class one, find the changepoints at the start
        cluster1_pieces = [pwl_pieces_list[idx] for idx in clustered_pwl_dict[cluster1_id]]
        class1_corner_set = set(chg_s for _, chg_s in cluster1_pieces)

        # for class two, find the changepoints at the end
        cluster2_pieces = [pwl_pieces_list[idx] for idx in clustered_pwl_dict[cluster2_id]]
        class2_corner_set = set(chg_e for chg_e, _ in cluster2_pieces)

        # compute the intersection of those points
        shared_change_points = class1_corner_set.intersection(class2_corner_set)

        # if there are any common change points
        if len(shared_change_points) > 0:

            loc1_name = construct_location_name(cluster1_id)
            loc2_name = construct_location_name(cluster2_id)

            # add an edge there, since it means the system was switching
            inferred_hybrid_system.add_edge(from_location=loc1_name, to_location=loc2_name)

            guard = init_lib.construct_guard_polyhedral_pwl(change_points_list=list(shared_change_points),
                                                            delta_diff=delta_fh)

            inferred_hybrid_system.set_guard(edge_tuple=(loc1_name, loc2_name), guard=guard)

    return inferred_hybrid_system


def meanshift_clustering(segment_flows_df, epsilon):
    """ This function clusters the slopes

    segment_flows_df must be a dataframe where rows are samples and columns are variables

    """

    # cluster the signal, meaning according to the bandwidth find the cluster centers of the kernel peaks
    ms = MeanShift(bandwidth=epsilon, seeds=None, bin_seeding=False)

    if len(segment_flows_df.shape) == 1:
        ms.fit(segment_flows_df.values.reshape(-1, 1))
    else:
        ms.fit(segment_flows_df.values)

    # form equivalence classes and sort the segments in respective equivalence centers
    clusters_dict = defaultdict(list)

    for idx, slope in segment_flows_df.iterrows():

        cluster_class = int(ms.predict(slope.values.reshape(1, -1)))

        clusters_dict[cluster_class].append(idx)

    return clusters_dict


def get_pwl_slopes(pwl_pieces_list):
    return [init_lib.get_slopes(piece_p1, piece_p2)
            for piece_p1, piece_p2 in pwl_pieces_list]


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")  # pragma: nocover
