import numpy as np


class SimpleMedian():
    def __init__(self, sigma_k) -> None:
        self.sigma_k = sigma_k
        self.center = (0, 0)

    def filter(self, points):
        self.center = points.mean(axis=0)
        
        distances = np.linalg.norm(points - self.center, axis=1)
        d_median = np.median(distances)
        d_std = distances.std()
        
        return points[np.abs(distances - d_median) < self.sigma_k*d_std]
