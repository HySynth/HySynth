from collections.abc import MutableMapping
from collections.abc import Iterable
from copy import deepcopy
import scipy.spatial as spt
import ppl

from hysynth.utils.hybrid_system import hybrid_system_base
from hysynth.utils.dynamics import Dyn
from hysynth.pwl.library import round_flow


class HybridSystemConvexHull(hybrid_system_base.HybridSystemBase):
    invariant_type = spt.ConvexHull
    guard_type = spt.ConvexHull

    def __init__(self, name, variables_names):
        super().__init__(name=name, variable_names=variables_names)
        if len(variables_names) < 2:
            raise ValueError("ConvexHulls need at least 2 dimensions, therefore, there must be at least 2 variables!")

    def set_invariant(self, location_name, invariant):
        """ Adds an invariant to a location """

        # location name must be a string
        if not isinstance(location_name, str):
            raise TypeError("Location name must be a string!")

        # first check if node exists
        if not self._graph.has_node(location_name):
            raise ValueError("No such location!")

        # check if it is typed
        if not isinstance(invariant, self.invariant_type):
            raise TypeError("The invariant must be a ConvexHull")

        # if all goes well, add it
        self._graph.nodes[location_name]["invariant"] = invariant

    def set_guard(self, edge_tuple, guard):
        """ Adds a guard to an edge """

        # guard tuple is a tuple of strings
        if not (isinstance(edge_tuple, tuple) and
                len(edge_tuple) == 2 and
                isinstance(edge_tuple[0], str) and
                isinstance(edge_tuple[1], str)):

            raise TypeError("Guard ID must be a 2-tuple of strings")

        # first check if egde exists
        if not self._graph.has_edge(*edge_tuple):
            raise ValueError("No such edge!")

        # check if it is typed
        if not isinstance(guard, self.guard_type):
            raise TypeError("Values of the guards must be ConvexHull")

        # if all goes well, add it
        self._graph.edges[edge_tuple]["guard"] = guard


class HybridSystemBoundaryCollections(hybrid_system_base.HybridSystemBase):
    def set_invariant(self, location_name, invariant):

        # now check that the invariant is a dictionary
        if not isinstance(invariant, MutableMapping):
            raise TypeError("Invariant must be a dictionary!")

        # now check that the variables match
        if not (set(invariant.keys()) == self.variables):
            raise ValueError("The invariant must include only and all the correct variables!")

        super().set_invariant(location_name=location_name, invariant=invariant)

    def set_guard(self, edge_tuple, guard):

        # now check that the guard is a dictionary
        if not isinstance(guard, MutableMapping):
            raise TypeError("Guard must be a dictionary!")

        # now check that the variables match
        if not (set(guard.keys()) == self.variables):
            raise ValueError("The guard must include only and all the correct variables!")

        super().set_guard(edge_tuple=edge_tuple, guard=guard)

    def set_flow(self, location_name, flow):
        # now check that the flow is a dictionary
        if not isinstance(flow, MutableMapping):
            raise TypeError("flow must be a dictionary!")

        # now check that the variables match
        if not (set(flow.keys()) == self.variables):
            raise ValueError("The flow must include only and all the correct variables!")

        super().set_flow(location_name=location_name, flow=flow)


class HybridSystemPolyhedral(hybrid_system_base.HybridSystemBase):
    """ This Hybrid System subclass enforces that the guards and invariants are polyhedra """

    def __init__(self, name, variable_names, delta=0):
        super().__init__(name=name, variable_names=variable_names)

        self._delta = delta

    @property
    def delta(self):
        return self._delta

    def set_invariant(self, location_name, invariant):

        # now check that the invariant is a dictionary
        if not isinstance(invariant, ppl.NNC_Polyhedron):    # apparently Polyhedron is not in the namespace
            raise TypeError("Invariant must be a NNC_Polyhedron!")

        super().set_invariant(location_name=location_name, invariant=invariant)

    def set_guard(self, edge_tuple, guard):

        # now check that the invariant is a dictionary
        if not isinstance(guard, ppl.NNC_Polyhedron):    # apparently Polyhedron is not in the namespace
            raise TypeError("Guard must be a NNC_Polyhedron!")

        super().set_guard(edge_tuple=edge_tuple, guard=guard)

    def set_flow(self, location_name, flow, rounding=False, skip_rounding=False):
        if not isinstance(flow, Iterable) and not isinstance(flow, Dyn):
            raise TypeError("flow must be an iterable!")

        if not isinstance(flow, Dyn):
            if rounding:
                flow = round_flow(flow)

            elif not skip_rounding and (flow != round_flow(flow)):
                raise ValueError("The flow is out of supported precision and must be rounded!")

        super().set_flow(location_name=location_name, flow=flow)

    def copy(self):
        """ Adding the delta to the ha """
        ha = super().copy()
        ha._delta = self.delta
        return ha

    def deepcopy(self):
        ha = super().deepcopy()
        ha._delta = self.delta
        return ha

    def __str__(self):
        to_be_printed = list()

        to_be_printed.append("\n\nHybrid System {}".format(self.name))
        to_be_printed.append("===================================================")

        for loc in self.locations:
            to_be_printed.append("Location: {}".format(loc))
            invariant = self.get_invariant(loc)
            if isinstance(invariant, ppl.NNC_Polyhedron):
                to_be_printed.append("Invariant: {}".format(invariant.constraints()))
            else:
                to_be_printed.append("Invariant: {}".format(invariant))
            to_be_printed.append("Flow: {}".format(self.flows[loc]))
            to_be_printed.append("---------------------------------------------------")

        to_be_printed.append("===================================================")
        for edge in self.edges:
            to_be_printed.append("---------------------------------------------------")
            to_be_printed.append("Edge: {} -> {}".format(edge[0], edge[1]))
            guard = self.get_guard(edge)
            if isinstance(guard, ppl.NNC_Polyhedron):
                to_be_printed.append("Guard: {}".format(guard.constraints()))
            else:
                to_be_printed.append("Guard: {}".format(guard))
        to_be_printed.append("")

        return "\n".join(to_be_printed)

    def __repr__(self):
        return str(self)


class JuliaSet(object):
    def __init__(self, X):
        self.X = X

    def deepcopy(self):
        # only one instance per Julia object required
        return self

    def __deepcopy__(self, memodict={}):
        return self.deepcopy()


class HybridSystemAffineDynamics(HybridSystemPolyhedral):
    """This is a subtype of the polyhedral hybrid automaton with affine ODEs"""

    def __init__(self, name, variable_names, delta):
        super().__init__(name=name, variable_names=variable_names, delta=delta)

    def deepcopy(self):
        # we share the name and also the variables because they do not change
        ha = HybridSystemAffineDynamics(name=self.name, variable_names=list(self.variables), delta=self.delta)
        # make a deep copy of the graph
        ha._graph = deepcopy(self._graph)
        return ha

    def get_invariant(self, location_name):
        wrapped_invariant = self.invariants[location_name]
        invariant = wrapped_invariant.X
        return invariant

    def set_invariant(self, location_name, invariant):
        wrapped_invariant = JuliaSet(invariant)
        self._graph.nodes[location_name]["invariant"] = wrapped_invariant

    def get_guard(self, edge_tuple):
        wrapped_guard = self.guards[edge_tuple]
        guard = wrapped_guard.X
        return guard

    def set_guard(self, edge_tuple, guard):
        wrapped_guard = JuliaSet(guard)
        self._graph.edges[edge_tuple]["guard"] = wrapped_guard


class HybridSystemNoInvariants(HybridSystemAffineDynamics):
    """This is a subtype of the polyhedral hybrid automaton without any invariants"""

    def __init__(self, hybrid_automaton):
        super().__init__(name=hybrid_automaton.name,
                         variable_names=list(hybrid_automaton.variables),
                         delta=hybrid_automaton.delta)
        self._graph = hybrid_automaton._graph

    def deepcopy(self):
        # we share the name and also the variables because they do not change
        ha = HybridSystemNoInvariants(self)
        # make a deep copy of the graph
        ha._graph = deepcopy(self._graph)
        return ha

    def get_invariant(self, location_name):
        return ppl.NNC_Polyhedron(len(self.variables) + 1, 'universe')

    def set_invariant(self, location_name, invariant):
        raise ValueError("Invariants cannot be set for an automaton with no constraints!")


class HybridSystemNoConstraints(HybridSystemNoInvariants):
    """This is a subtype of the polyhedral hybrid automaton without any constraints"""

    def __init__(self, hybrid_automaton):
        super().__init__(hybrid_automaton)

    def deepcopy(self):
        # we share the name and also the variables because they do not change
        ha = HybridSystemNoConstraints(self)
        # make a deep copy of the graph
        ha._graph = deepcopy(self._graph)
        return ha

    def get_guard(self, edge_tuple):
        return ppl.NNC_Polyhedron(len(self.variables) + 1, 'universe')

    def set_guard(self, edge_tuple, guard):
        raise ValueError("Guards cannot be set for an automaton with no constraints!")


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly!")  # pragma: nocover
