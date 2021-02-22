from .SetRep import SetRep


class BallInf(SetRep):
    def __init__(self, center, radius):
        self._center = center
        self._radius = radius
