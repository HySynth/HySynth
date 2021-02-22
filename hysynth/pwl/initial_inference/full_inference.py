# standard libraries
import datetime
import itertools
from collections import defaultdict

# external libraries
import pandas as pd
from sklearn.cluster import MeanShift

# internal libraries
from hysynth.utils.hybrid_system import HybridSystemPolyhedral
from hysynth.pwl.library import check_clustering_bandwidth
from hysynth.utils.hybrid_system.library import construct_variable_name
from hysynth.pwl.initial_inference import lib as init_lib


def infer_hybrid_system_polyhedral_pwl_full_dataset(pwl_dataset,
                                                    delta_ha,
                                                    delta_fh,
                                                    epsilon_meanshift=False,
                                                    hybrid_system_name=None):
    """ This function is the initial hybrid system inference function """

    # some safety and integrity checks since this is the outer interface function
    if not isinstance(pwl_dataset, list) and all([isinstance(pwl_l, list) for pwl_l in pwl_dataset]):
        raise TypeError("The variable <pwl_dataset> must be a list of lists!")

    check_clustering_bandwidth(epsilon_meanshift)

    if not isinstance(delta_fh, (float, int)):
        raise TypeError("The argument <delta_fh> must be numeric!")

    if not isinstance(delta_ha, (float, int)):
        raise TypeError("The argument <delta_fh> must be numeric!")

    if hybrid_system_name is None:
        curr_datetime = datetime.datetime.now()
        hybrid_system_name = "test_hs_{month}{day}{hour}{minute}".format(month=curr_datetime.month,
                                                                         day=curr_datetime.day,
                                                                         hour=curr_datetime.hour,
                                                                         minute=curr_datetime.minute)

    else:
        if not isinstance(hybrid_system_name, str):
            raise TypeError("The argument <hybrid_system_name> must be a string!")

    if epsilon_meanshift is False:
        raise NotImplementedError("Makes no sense to not cluster!")

    variable_names_list = [construct_variable_name(1)]

    # initialize the hybrid system that we are trying to construct
    inferred_hybrid_system = HybridSystemPolyhedral(name=hybrid_system_name,
                                                    variable_names=variable_names_list,
                                                    delta=delta_ha)

    all_pwl_pieces = list()

    for pwl_list in pwl_dataset:
        all_pwl_pieces.append(list(zip(pwl_list[0:-1], pwl_list[1:])))

    pwl_slopes_df = get_pwl_pieces_slopes_df(all_pwl_pieces=all_pwl_pieces)

    clustered_pwl_dict = meanshift_clustering(segment_flows_df=pwl_slopes_df,
                                              epsilon=epsilon_meanshift)

    # start building the Hybrid System, starting with locations, invariants and flows
    for cluster_id, cluster_segments_ids in clustered_pwl_dict.items():

        location_name = "Q{}".format(str(cluster_id))

        # for each cluster, make a mode/location
        inferred_hybrid_system.add_location("Q{}".format(str(cluster_id)))

        # separate out the pwl pieces belonging to this class
        cluster_pieces = [all_pwl_pieces[idx[0]][idx[1]] for idx in cluster_segments_ids]

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
        cluster1_pieces = [all_pwl_pieces[idx[0]][idx[1]] for idx in clustered_pwl_dict[cluster1_id]]
        class1_corner_set = set(chg_s for _, chg_s in cluster1_pieces)

        # for class two, find the changepoints at the end
        cluster2_pieces = [all_pwl_pieces[idx[0]][idx[1]] for idx in clustered_pwl_dict[cluster2_id]]
        class2_corner_set = set(chg_e for chg_e, _ in cluster2_pieces)

        # compute the intersection of those points
        shared_change_points = class1_corner_set.intersection(class2_corner_set)

        # if there are any common change points
        if len(shared_change_points) > 0:

            loc1_name = "Q{}".format(str(cluster1_id))
            loc2_name = "Q{}".format(str(cluster2_id))

            # add an edge there, since it means the system was switching
            inferred_hybrid_system.add_edge(from_location=loc1_name, to_location=loc2_name)

            guard = init_lib.construct_guard_polyhedral_pwl(change_points_list=shared_change_points,
                                                            delta_diff=delta_fh)

            inferred_hybrid_system.set_guard(edge_tuple=(loc1_name, loc2_name), guard=guard)

    return inferred_hybrid_system


def meanshift_clustering(segment_flows_df, epsilon):

    # cluster the signal, meaning according to the bandwidth find the cluster centers of the kernel peaks
    ms = MeanShift(bandwidth=epsilon, seeds=None, bin_seeding=False)

    if len(segment_flows_df.shape) == 1:
        ms.fit(segment_flows_df[["slopes"]].values.reshape(-1, 1))
    else:
        ms.fit(segment_flows_df[["slopes"]].values)

    # form equivalence classes and sort the segments in respective equivalence centers
    clusters_dict = defaultdict(list)

    for piece_idx, series in segment_flows_df.iterrows():

        slope = series["slopes"]
        ts_idx = int(series["ts_idx"])

        cluster_class = int(ms.predict(slope))

        clusters_dict[cluster_class].append((ts_idx, piece_idx))

    return clusters_dict


def get_pwl_pieces_slopes_df(all_pwl_pieces):

    final_df = pd.DataFrame()

    for idx, pwl_piece_set in enumerate(all_pwl_pieces):
        slopes = [init_lib.get_slopes(piece_p1, piece_p2) for piece_p1, piece_p2 in pwl_piece_set]

        temp_df = pd.DataFrame(dict(slopes=slopes, ts_idx=idx))

        final_df = final_df.append(temp_df)

    return final_df






if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")  # pragma: nocover
