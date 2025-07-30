import numpy as np
from causalboundingengine.algorithms.algorithm import Algorithm

class TianPearl(Algorithm):
    def _compute_ATE(self, X: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
        p1 = np.mean(Y[X == 1]) if np.any(X == 1) else 0.0
        p0 = np.mean(Y[X == 0]) if np.any(X == 0) else 0.0

        # Bounds on P(Y=1 | do(X=1)) and do(X=0)
        lower_do1 = p1
        upper_do1 = 1 - p0
        lower_do0 = p0
        upper_do0 = 1 - p1

        # ATE bounds are differences of those intervals
        lower = lower_do1 - upper_do0
        upper = upper_do1 - lower_do0

        return min(lower, upper), max(lower, upper)
    
    def _compute_PNS(self, X: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
        # Nonparametric bounds without assuming exogeneity
        p_xy = np.mean((X == 1) & (Y == 1))
        p_x0y0 = np.mean((X == 0) & (Y == 0))

        lower = 0.0
        upper = p_xy + p_x0y0

        return lower, upper
