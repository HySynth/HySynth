import numpy as np
from random import random, randint
from copy import deepcopy

from .Dyn import Dyn


class ConstDyn(Dyn):
    def __init__(self, b):
        if not isinstance(b, np.ndarray):
            assert isinstance(b, list)
            b = np.array(b)
        self._b = b

    def A(self):
        n = self.dim()
        return np.zeros((n, n))

    def b(self):
        return self._b

    def __str__(self):
        return "x' = {}".format(self._b)

    def dim(self):
        return self._b.shape[0]

    def successor(self, t, x0):
        x1 = self._b * t + x0
        return x1

    def perturb(self, max_perturbation):
        if max_perturbation == 0.0:
            return self
        b = deepcopy(self._b)
        for j in range(self.dim()):
            v = b[j]
            if v != 0.0:
                sign = 1 if randint(0, 1) > 0 else -1
                change = random() * max_perturbation * sign
                b[j] += change
        return ConstDyn(b)
