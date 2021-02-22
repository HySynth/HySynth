from collections import namedtuple
from collections.abc import MutableMapping

Boundary = namedtuple("Boundary", ["upper", "lower"])
Flowtube = namedtuple("Flowtube", ["slope", "delta"])


class BoundaryCollection(MutableMapping):

    def __init__(self, boundary_dict):
        self._boundary_store = dict()

        if not isinstance(boundary_dict, dict):
            raise TypeError("Must pass a dictionary!")

        for variable_name, bound in boundary_dict.items():

            if isinstance(bound, Boundary):
                self._boundary_store[variable_name] = bound

            elif isinstance(bound, tuple) and len(bound) == 2:
                self._boundary_store[variable_name] = Boundary(*bound)

            else:
                raise TypeError("Values of the dict must be either tuples with 2 values or a Boundary object")

    def __setitem__(self, key, value) -> None:
        if key not in self.variables:
            raise KeyError("Cannot add variables on the fly!")

        if not isinstance(value, Boundary) and not (isinstance(value, tuple) and len(value) == 2):
            raise TypeError("Value must a valid tuple or a Flowtube object!")

        if isinstance(value, tuple):
            if isinstance(value, Boundary):
                self._boundary_store[key] = value
            else:
                self._boundary_store[key] = Boundary(*value)

    def __delitem__(self, v):
        raise NotImplementedError("Not allowed to delete things this way!")

    def __getitem__(self, key):
        if key not in self.variables:
            raise KeyError("No such variable!")

        return self._boundary_store[key]

    def __len__(self) -> int:
        return len(self._boundary_store)

    def __iter__(self):
        return iter(self._boundary_store)

    @property
    def variables(self):
        return list(self._boundary_store.keys())

    @property
    def dim(self):
        return len(self.variables)

    def __str__(self):
        return "\n".join([f"Variable ({variable}): "
                          f"upper limit: {boundary.upper}, "
                          f"lower: {boundary.lower}"
                          for variable, boundary in self._boundary_store.items()])

    def __repr__(self):
        return str(self._boundary_store)


class FlowtubeCollection(MutableMapping):

    def __init__(self, flowtube_dict: dict):
        self._flowtube_store = dict()

        if not isinstance(flowtube_dict, dict):
            raise TypeError("Must pass a dictionary!")

        for variable_name, flowtube in flowtube_dict.items():

            if isinstance(flowtube, Flowtube):
                self._flowtube_store[variable_name] = flowtube

            elif isinstance(flowtube, tuple) and len(flowtube) == 2:
                self._flowtube_store[variable_name] = Flowtube(*flowtube)

            else:
                raise TypeError("Values of the dict must be either tuples with 2 values or a Boundary object")

    def __setitem__(self, key, value) -> None:
        if key not in self.variables:
            raise KeyError("Cannot add variables on the fly!")

        if not isinstance(value, Flowtube) and not (isinstance(value, tuple) and len(value) == 2):
            raise TypeError("Value must a valid tuple or a Flowtube object!")

        if isinstance(value, Flowtube):
            self._flowtube_store[key] = value
        else:
            self._flowtube_store[key] = Flowtube(*value)

    def __delitem__(self, v):
        raise NotImplementedError("Not allowed to delete things this way!")

    def __getitem__(self, key):
        if key not in self.variables:
            raise KeyError("No such variable!")

        return self._flowtube_store[key]

    def __len__(self) -> int:
        return len(self._flowtube_store)

    def __iter__(self):
        return iter(self._flowtube_store)

    @property
    def variables(self):
        return list(self._flowtube_store.keys())

    @property
    def dim(self):
        return len(self.variables)

    def __str__(self):
        return "\n".join([f"Variable ({variable}): "
                          f"slope: {flowtube.slope}, "
                          f"delta: {flowtube.delta}"
                          for variable, flowtube in self._flowtube_store.items()])

    def __repr__(self):
        return str(self._flowtube_store)
