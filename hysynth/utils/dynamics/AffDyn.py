import numpy as np

from .Dyn import Dyn
from .ConstDyn import ConstDyn
from .LinDyn import LinDyn


class AffDyn(Dyn):
    def __init__(self, A, b):
        if not isinstance(A, np.ndarray):
            A = np.array(A)
        if not isinstance(b, np.ndarray):
            b = np.array(b)
        self._A = A
        self._b = b

    def A(self):
        return self._A

    def b(self):
        return self._b

    def __str__(self):
        return "x' = {}x + {}".format(self._A, self._b)

    def dim(self):
        return self._b.shape[0]

    def successor(self, t, x0):
        # make affine system linear by extending the dimension to [A b; 0 0] and x0' = [x0 1]
        A_high = np.block([[np.concatenate((self._A, self._b.reshape(-1, 1)), axis=1)], [np.zeros(self.dim() + 1)]])
        x0_high = np.hstack([x0, 1.0])
        dyn = LinDyn(A_high)
        x1_high = dyn.successor(t, x0_high)
        x1 = x1_high[0:-1]
        return x1

    def perturb(self, max_perturbation):
        if max_perturbation == 0.0:
            return self
        A = LinDyn(self._A).perturb(max_perturbation).A()
        b = ConstDyn(self._b).perturb(max_perturbation).b()
        return AffDyn(A, b)
