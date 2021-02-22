from .SetRep import SetRep


class HPolyhedron(SetRep):
    def __init__(self, constraints):
        self._constraints = constraints
