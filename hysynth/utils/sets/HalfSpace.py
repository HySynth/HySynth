from .SetRep import SetRep


class HalfSpace(SetRep):
    def __init__(self, a, b):
        self._a = a
        self._b = b
