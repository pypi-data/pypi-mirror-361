import cv2

import numpy as np

from ..localizers import Find
from ..prepocessing import image_preprocessing

class HoughTransform():
    def __init__(self, mode: int,
                 hough_param2=30,
                 preprocess: bool = True) -> None:
        assert mode in [Find.Pupil, Find.Iris], "Wrong mode value. Use one of: irisloc.FIND_PUPIL, irisloc.FIND_IRIS"
        self.mode = mode
        
        self.hough_param2=hough_param2
        
        self.preprocess = preprocess
        
        if mode == Find.Pupil:
            self.min_radius=8
            self.max_radius=36
        elif mode == Find.Iris:
            self.min_radius=36
            self.max_radius=64
        
        # Предвычисляем тригонометрические значения
        self.theta_range = np.arange(0, 360)
        self.cos_theta = np.cos(self.theta_range * np.pi / 180)
        self.sin_theta = np.sin(self.theta_range * np.pi / 180)

    def find(self, source):
        if self.preprocess:
            img = image_preprocessing(source)
        
        # Edge detection
        edges = cv2.Canny(img.astype(np.uint8), 128, 255)
        height, width = edges.shape
        
        # Находим все точки границ сразу
        edge_points = np.column_stack(np.where(edges > 0))
        
        if len(edge_points) == 0:
            return (0, 0), 0
            
        accumulator = np.zeros((height, width, self.max_radius - self.min_radius))
        
        # Векторизованное вычисление для всех радиусов и углов
        for r_idx, r in enumerate(range(self.min_radius, self.max_radius)):
            # Вычисляем смещения для всех углов сразу
            a_offsets = (r * self.cos_theta).astype(int)
            b_offsets = (r * self.sin_theta).astype(int)
            
            # Для каждой точки границы
            for y, x in edge_points:
                # Вычисляем все возможные центры для данного радиуса
                a_centers = x - a_offsets
                b_centers = y - b_offsets
                
                # Фильтруем валидные центры
                valid_mask = (
                    (a_centers >= 0) & (a_centers < width) & 
                    (b_centers >= 0) & (b_centers < height)
                )
                
                # Обновляем аккумулятор
                valid_a = a_centers[valid_mask]
                valid_b = b_centers[valid_mask]
                
                np.add.at(accumulator, (valid_b, valid_a, r_idx), 1)
        
        # Find the best circle
        max_accumulator = np.unravel_index(np.argmax(accumulator), accumulator.shape)
        best_y, best_x, best_r = max_accumulator
        best_r += self.min_radius

        return (best_x, best_y), best_r