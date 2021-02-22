from .SetRep import SetRep


class Interval(SetRep):
    def __init__(self, lo, hi):
        self._lo = lo
        self._hi = hi
