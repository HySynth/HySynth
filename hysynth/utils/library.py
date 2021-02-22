import pickle
import errno
import os
from pathlib import Path


MODEL_SAVE_PATH = Path(__file__).parent.parent.parent / "data" / "saved_models"


def create_folders(path):
    # from https://stackoverflow.com/a/12517490
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def save_to_file(obj, file_name, path=MODEL_SAVE_PATH):
    create_folders(path)
    with open(f'{path}/{file_name}.pickle', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_from_file(file_name, path=MODEL_SAVE_PATH):
    with open(f'{path}/{file_name}.pickle', 'rb') as f:
        return pickle.load(f)


def max_search_tree_nodes(n_modes, n_pieces):
    if n_pieces == 0:
        return 0

    value2count = {n_modes: 1}
    total_sum = 0
    for k in range(n_pieces):
        value2count_new = dict()
        for value, count in value2count.items():
            count_tmp = value2count_new.get(value, 0)
            count_tmp += value * count
            value2count_new[value] = count_tmp

            value_plus_one = value + 1
            count_tmp = value2count_new.get(value_plus_one, 0)
            count_tmp += count
            value2count_new[value_plus_one] = count_tmp

        value2count = value2count_new
        total_sum += sum(value2count.values())

    return total_sum


def max_search_tree_nodes_explicit(n_modes, n_pieces):
    # explicit construction of the tree; only scalable for small values
    if n_pieces == 0:
        return 0

    # first layer
    layer0 = [n_modes]
    layers = [layer0]

    # other layers
    while len(layers) < n_pieces + 1:
        old_layer = layers[-1]
        new_layer = []
        layers.append(new_layer)
        for node in old_layer:
            for i in range(node):
                new_layer.append(node)
            new_layer.append(node+1)

    n_nodes = 0
    for layer in layers[1:]:
        n_nodes += len(layer)
    return n_nodes


def argmax_list(list):
    f = lambda i: list[i]
    return max(range(len(list)), key=f)


def argmin_list(list):
    f = lambda i: list[i]
    return min(range(len(list)), key=f)


def argmins_list(list):
    if not list:
        return []

    minimum_value = list[0]
    minimum_list = [0]
    for i, e in enumerate(list[1:]):
        if e < minimum_value:
            minimum_value = e
            minimum_list = [i]
        elif e == minimum_value:
            minimum_list.append(i)
    return minimum_list
