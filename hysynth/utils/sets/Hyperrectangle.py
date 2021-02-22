from .SetRep import SetRep


class Hyperrectangle(SetRep):
    def __init__(self, center, radius):
        self._center = center
        self._radius = radius
