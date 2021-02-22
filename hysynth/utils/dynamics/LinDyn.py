import numpy as np
from scipy.linalg import expm
from random import random, randint
from copy import deepcopy

from .Dyn import Dyn


class LinDyn(Dyn):
    def __init__(self, A):
        if not isinstance(A, np.ndarray):
            A = np.array(A)
        self._A = A

    def A(self):
        return self._A

    def b(self):
        return np.zeros(self.dim())

    def __str__(self):
        return "x' = {}x".format(self._A)

    def dim(self):
        return self._A.shape[0]

    def successor(self, t, x0):
        x1 = np.dot(expm(self._A * t), x0)
        return x1

    def perturb(self, max_perturbation):
        if max_perturbation == 0.0:
            return self
        A = deepcopy(self._A)
        for row in A:
            for j in range(len(row)):
                v = row[j]
                if v != 0.0:
                    sign = 1 if randint(0, 1) > 0 else -1
                    change = random() * max_perturbation * sign
                    row[j] += change
        return LinDyn(A)
