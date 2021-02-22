""" This module contains the Hybrid System AbstractBaseClass and the base class providing the base interface """
# standard library modules
import pickle
from abc import ABCMeta, abstractmethod
from copy import deepcopy
import networkx as nx

from hysynth.utils.library import MODEL_SAVE_PATH, create_folders


class HybridSystemABC(metaclass=ABCMeta):
    """ This is the Abstract Base Class for the Hybrid System definition

    The purpose of this class is to provide and ensure the interface for all the HybridSystem subclasses
    It has no implementation because it only serves as a scaffold

    """

    @property
    def locations(self):
        raise NotImplementedError()  # pragma: nocover

    @property
    def edges(self):
        raise NotImplementedError()  # pragma: nocover

    @property
    def flows(self):
        raise NotImplementedError()  # pragma: nocover

    @property
    def invariants(self):
        raise NotImplementedError()  # pragma: nocover

    @property
    def guards(self):
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def add_location(self, location_name):
        """ Adds a location """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def remove_location(self, location_name):
        """ Removes the location """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def add_edge(self, from_location, to_location):
        """ Adds an edge """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def remove_edge(self, from_location, to_location):
        """ Removes an edge """
        raise NotImplementedError()  # pragma: nocover

    def unroll(self, n_transitions):
        """ Unrolls the path: provides all possible paths of n_transitions number of transitions """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def set_invariant(self, location_name, invariant):
        """ Adds an invariant to a location """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def get_invariant(self, location_name):
        """ Returns an invariant object """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def remove_invariant(self, location_name):
        """ Removes an invariant """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def set_guard(self, edge_tuple, guard):
        """ Adds a guard to an edge """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def get_guard(self, edge_tuple):
        """ Returns a guard object """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def remove_guard(self, edge_tuple):
        """ Removes a guard """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def accepts_path(self, path):
        """ Checks if a path is valid """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def set_flow(self, location_name, flow):
        """ Adds flow to a location """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def get_flow(self, location_name):
        """ Returns a flow object """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def remove_flow(self, location_name):
        """ Removes the flow """
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def save(self, filename, path):
        """ This function saves the Hybrid System instance using pickle """
        raise NotImplementedError()  # pragma: nocover

    @staticmethod
    @abstractmethod
    def load(filename, path):
        """ This function loads a Hybrid System"""
        raise NotImplementedError()  # pragma: nocover

    @abstractmethod
    def copy(self):
        """ This provides a copy of the Hybrid Automaton """
        raise NotImplementedError()  # pragma: nocover


class HybridSystemBase(HybridSystemABC):
    """ This is the Hybrid System Base class, it is the class which all HybridSystem classes should inherit from

    It provides the very basic implementations of:
        - the interface
        - most of the helper functions
        - underlying data structures
        - basic properties

    """

    def __init__(self, name, variable_names):
        if not isinstance(name, str):
            raise TypeError("Name of the Hybrid System must be a string")

        if not isinstance(variable_names, list):
            raise TypeError("Variable names must be a list!")

        if not all(map(lambda x: isinstance(x, str), variable_names)):
            raise TypeError("Variable names must all be strings!")

        if len(set(variable_names)) != len(variable_names):
            raise ValueError("Variable names must be unique, no repeats!")

        self.name = name
        self._variables = set(variable_names)
        self._graph = nx.DiGraph()

    def __str__(self):
        to_be_printed = list()

        to_be_printed.append("\n\nHybrid System \nName: {}".format(self.name))
        to_be_printed.append("===================================================")

        for loc in self.locations:
            to_be_printed.append("Location: {}".format(loc))
            to_be_printed.append("Invariant: {}".format(self.invariants[loc]))
            to_be_printed.append("Flow: {}".format(self.flows[loc]))
            to_be_printed.append("---------------------------------------------------")

        to_be_printed.append("===================================================")
        for edge in self.edges:
            to_be_printed.append("---------------------------------------------------")
            to_be_printed.append("Edge: {} -> {}".format(edge[0], edge[1]))
            to_be_printed.append("Guard: {}".format(self.guards[edge]))

        return "\n".join(to_be_printed)

    # region Properties

    @property
    def variables(self):
        return self._variables

    @property
    def dim(self):
        return len(self.variables)

    @property
    def locations(self):
        return list(self._graph.nodes())

    @property
    def edges(self):
        return list(self._graph.edges())

    @property
    def flows(self):
        return dict(self._graph.nodes(data='flow', default=False))

    @property
    def invariants(self):
        return dict(self._graph.nodes(data='invariant', default=False))

    @property
    def guards(self):
        return {(e1, e2): g for e1, e2, g in self._graph.edges(data='guard', default=False)}

    # endregion

    # region Locations

    def add_location(self, location_name):
        """
        Adds a location

        :param location_name: The name of the location
        :return:
        """
        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        if location_name not in self.locations:
            self._graph.add_node(location_name)
        else:
            raise ValueError("Location already exists!")

    def remove_location(self, location_name):
        """ Removes the location """

        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        if location_name in self.locations:
            self._graph.remove_node(location_name)
        else:
            raise KeyError("Location does not exist!")

    # endregion

    # region Edges

    def add_edge(self, from_location, to_location):
        """ Adds an edge """

        if not (isinstance(from_location, str) and isinstance(to_location, str)):
            raise TypeError("Locations must be strings!")

        if from_location in self.locations and to_location in self.locations:
            self._graph.add_edge(from_location, to_location)
        else:
            raise KeyError("Locations do not exist!")

    def remove_edge(self, from_location, to_location):
        """ Removes an edge """

        if not (isinstance(from_location, str) and isinstance(to_location, str)):
            raise TypeError("Locations must be strings!")

        if self._graph.has_edge(from_location, to_location):
            self._graph.remove_edge(from_location, to_location)

        else:
            raise KeyError("No such edge!")

    def unroll(self, n_transitions):
        """ Get all the possible paths with n_transitions number of transitions """
        return get_all_k_paths(graph=self._graph, n_transitions=n_transitions)

    # endregion

    # region Invariants

    def set_invariant(self, location_name, invariant):
        """ Adds an invariant to a location """

        # location name must be a string
        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        # first check if node exists
        if not self._graph.has_node(location_name):
            raise ValueError("No such location!")

        # if all goes well, add it
        self._graph.nodes[location_name]["invariant"] = invariant

    def get_invariant(self, location_name):
        """ Returns an invariant object """

        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        if not self._graph.has_node(location_name):
            raise ValueError("No such location!")

        invariant = self.invariants[location_name]

        if not invariant:
            raise ValueError("Location does not have an invariant defined!")

        return invariant

    def remove_invariant(self, location_name):
        """ Removes an invariant """

        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        if self._graph.has_node(location_name):
            del self._graph.nodes[location_name]["invariant"]

        else:
            raise ValueError("No such location!")

    # endregion

    # region Guards

    def set_guard(self, edge_tuple, guard):
        """ Adds a guard to an edge """

        # guard tuple is a tuple of strings
        if not (isinstance(edge_tuple, tuple) and
                len(edge_tuple) == 2 and
                isinstance(edge_tuple[0], str) and
                isinstance(edge_tuple[1], str)):

            raise TypeError("Guard ID must be a 2-tuple of strings")

        # first check if edge exists
        if not self._graph.has_edge(*edge_tuple):
            raise ValueError("No such edge!")

        # if all goes well, add it
        self._graph.edges[edge_tuple]["guard"] = guard

    def get_guard(self, edge_tuple):
        """ Returns a guard object """

        if not (isinstance(edge_tuple, tuple) and
                len(edge_tuple) == 2 and
                isinstance(edge_tuple[0], str) and
                isinstance(edge_tuple[1], str)):

            raise TypeError("Guard ID must be a 2-tuple of strings")

        if not self._graph.has_edge(*edge_tuple):
            raise ValueError("No such edge!")

        guard = self.guards[edge_tuple]

        if not guard:
            raise ValueError("Edge does not have a guard defined!")

        return guard

    def remove_guard(self, edge_tuple):
        """ Removes a guard """
        if self._graph.has_edge(*edge_tuple):
            del self._graph.edges[edge_tuple]["guard"]
        else:
            raise ValueError("No such edge!")

    def find_outgoing_edges(self, location_name):
        """ Outputs all the outgoing edges for a location """

        if not isinstance(location_name, str):
            raise TypeError("location_name must be a string")

        if not self._graph.has_node(location_name):
            raise ValueError("No such location: {}".format(location_name))

        return [edge[1] for edge in self._graph.out_edges(location_name)]

    def find_incoming_edges(self, location_name):
        """ Outputs all the incoming edges for a location """

        if not isinstance(location_name, str):
            raise TypeError("location_name must be a string")

        if not self._graph.has_node(location_name):
            raise ValueError("No such location!")

        return [edge[1] for edge in self._graph.in_edges(location_name)]

    def find_all_edges(self, location_name):
        """ Outputs all edges for a location """

        if not isinstance(location_name, str):
            raise TypeError("location_name must be a string")

        if not self._graph.has_node(location_name):
            raise ValueError("No such location!")

        return [edge[1] for edge in self._graph.edges(location_name)]

    def accepts_path(self, path):
        if not isinstance(path, list):
            raise TypeError("Path must be a list")

        if not all(map(lambda x: isinstance(x, str), path)):
            raise TypeError("Path must be a list of strings!")

        if not all(map(lambda x: x in self.locations, path)):
            raise ValueError("Path contains invalid locations!!")

        return all(map(self._graph.has_edge, path, path[1:]))

    # endregion

    # region Flow

    def set_flow(self, location_name, flow):
        """ Adds flow to a location """

        # location name must be a string
        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        # first check if node exists
        if not self._graph.has_node(location_name):
            raise ValueError("No such location!")

        # if all goes well, add it
        self._graph.nodes[location_name]["flow"] = flow

    def get_flow(self, location_name):
        """ Returns a flow object """

        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        if not self._graph.has_node(location_name):
            raise ValueError("No such location: {}".format(location_name))

        flow = self.flows[location_name]
        if flow is False:
            raise ValueError("Location does not have a flow defined!")

        return flow

    def remove_flow(self, location_name):
        """ Removes the flow """

        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        if self._graph.has_node(location_name):
            del self._graph.nodes[location_name]["flow"]
        else:
            raise ValueError("No such location!")

    # endregion

    # region Support Functions

    def has_edge(self, to_location, from_location):
        """ Returns if an edge exists """
        return self._graph.has_edge(to_location, from_location)

    def save(self, filename="", path=MODEL_SAVE_PATH):
        """ This function saves the Hybrid System instance using pickle """
        if filename == "":
            filename = f"{self.name}"
        create_folders(path)
        with open(f'{path}/{filename}.pickle', 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(filename, path=MODEL_SAVE_PATH):
        """ This function loads a Hybrid System"""
        with open(f'{path}/{filename}.pickle', 'rb') as f:
            return pickle.load(f)

    def convert_automaton(self, conversion_function_flow, conversion_function_set):
        ha = self.deepcopy()

        for loc in ha.locations:
            if conversion_function_flow is not None:
                flow_new = conversion_function_flow(ha.get_flow(loc))
                ha.set_flow(location_name=loc, flow=flow_new)

            inv_new = conversion_function_set(ha.get_invariant(loc))
            ha.set_invariant(location_name=loc, invariant=inv_new)

        for t in ha.edges:
            guard_new = conversion_function_set(ha.get_guard(t))
            ha.set_guard(edge_tuple=t, guard=guard_new)

        return ha

    def copy(self):
        """ This function is used to copy the Hybrid System.

        It creates a new instance, fills the same values and returns it

        """
        # get the variables
        variable_names = self.variables.copy()

        # use the previous name
        hs_name = self.name

        # now create a new instance using those variables, use __class__ method to create the same type of instance
        new_hs = self.__class__(name=str(hs_name),
                                variable_names=list(variable_names))

        # copy the old graph to the new graph
        new_hs._graph = deepcopy(self._graph)

        return new_hs

    def deepcopy(self):
        # use the previous name
        hs_name = self.name

        # we share the variables because they do not change
        variable_names = self.variables

        # now create a new instance using those variables, use __class__ method to create the same type of instance
        new_hs = self.__class__(name=str(hs_name),
                                variable_names=list(variable_names))

        # copy the old graph to the new graph
        new_hs._graph = deepcopy(self._graph)

        return new_hs


def _find_paths(graph, root_node, n_transitions):
    """ Returns a list of paths with n_transitions transitions from root node

    graph: Is the nx.Graph object which contains the (V, E) graph
    root_node: it is the node from which we start
    n_transitions: is the number of transitions
    """

    # recursion base case
    if n_transitions == 0:
        return [[root_node]]

    paths = []
    for neighbor in graph.successors(root_node):

        # recursive step
        for path in _find_paths(graph, neighbor, n_transitions - 1):
            paths.append([root_node] + path)

    return paths


def get_all_k_paths(graph, n_transitions):
    """ This function returns all the possible paths with n_transitions number of transitions """

    if not isinstance(graph, nx.DiGraph):
        raise TypeError("graph must be a directed graph -> nx.DiGraph")

    if not (isinstance(n_transitions, int) and n_transitions >= 0):
        raise TypeError("n_transitions must be a non-negative integer")

    allpaths = []
    for node in graph:
        allpaths.extend(_find_paths(graph, node, n_transitions))

    if len(allpaths) > 0:
        return allpaths

    # should raise error since later functions can reasonably expect to use this path list
    else:
        raise ValueError("There was no paths of n_transitions number of transitions!")


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")  # pragma nocover
