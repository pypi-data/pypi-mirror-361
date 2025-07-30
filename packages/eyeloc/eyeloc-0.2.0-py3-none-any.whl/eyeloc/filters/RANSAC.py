import numpy as np
from cv2 import fitEllipse

from ..fitting import fitCircleLS, ellipse_distance


class CircleRANSAC():
    def __init__(self, distance, inliers, max_iter, __return_best_candidate = False) -> None:
        self.distance = distance
        self.inliers = inliers
        self.max_iter = max_iter

        self.__return_best_candidate = __return_best_candidate
        
        # Предвычисляем случайные выборки
        self._precompute_random_samples()
        
    def _precompute_random_samples(self):
        """Предвычисляем случайные выборки для ускорения"""
        self._random_samples = []
        for seed in range(self.max_iter):
            np.random.seed(seed)
            self._random_samples.append(np.random.randint(0, 1000, 3))
    
    def filter(self, points):
        best_mse = 10000
        best_sample_ind = []
        
        for i in range(min(self.max_iter, len(self._random_samples))):
            # Используем предвычисленные индексы
            sample_indices = self._random_samples[i] % len(points)
            
            circle_center, circle_radius = fitCircleLS(points[sample_indices])
            
            # Векторизованное вычисление расстояний
            point_distances = np.abs(np.linalg.norm(points - circle_center, axis=1) - circle_radius)
            inliers_mask = point_distances < self.distance
            
            if np.sum(inliers_mask) >= self.inliers:
                mse = np.mean(point_distances[inliers_mask]**2)
                if mse < best_mse:
                    best_mse = mse
                    best_center, best_radius = circle_center, circle_radius
                    best_sample_ind = np.where(inliers_mask)[0]
                    
        if not self.__return_best_candidate:
            return points[best_sample_ind]
        else:
            circle_center, circle_radius = fitCircleLS(points[best_sample_ind])
            return points[best_sample_ind], (best_center, best_radius, best_mse)

class EllipseRANSAC():
    def __init__(self, distance, inliers, max_iter, __return_best_candidate = False) -> None:
        self.distance = distance
        self.inliers = inliers
        self.max_iter = max_iter
        
        self.__return_best_candidate = __return_best_candidate
        
    def filter(self, points):
        best_mse = 10000
        best_sample_ind = []
        for _ in range(self.max_iter):
            random_sample_indeces = np.random.choice(len(points), 5, replace=False)
            ((centx,centy), (width,height), angle) = fitEllipse(points[random_sample_indeces].astype(np.float32))
            inliers_ind = []
            distances = []
            for i in range(len(points)):
                point_distance = ellipse_distance(points[i], centx, centy, width, height, np.deg2rad(angle))
                if point_distance < self.distance:
                    inliers_ind.append(i)
                    distances.append(point_distance)
            if len(inliers_ind) >= self.inliers:
                mse = np.power(distances, 2).mean()
                if mse < best_mse:
                    best_mse = mse
                    best_center, best_width, best_height, best_angle, best_sample_ind = (centx, centy), width, height, angle, inliers_ind

        if not self.__return_best_candidate:
            return np.array(points[best_sample_ind]).astype(np.float32)
        else:
            ((centx,centy), (width,height), angle) = fitEllipse(points[random_sample_indeces].astype(np.float32))
            return np.array(points[best_sample_ind]).astype(np.float32), (best_center, best_width, best_height, best_angle)