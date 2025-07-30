import numpy as np
from causalboundingengine.algorithms.algorithm import Algorithm

class Manski(Algorithm):
    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
        p1 = np.mean(Y[X == 1]) if np.any(X == 1) else 0.0
        p0 = np.mean(Y[X == 0]) if np.any(X == 0) else 0.0

        lower = max(p1 - p0 - 1, -1)
        upper = min(p1 - p0 + 1,  1)

        return min(lower, upper), max(lower, upper)
