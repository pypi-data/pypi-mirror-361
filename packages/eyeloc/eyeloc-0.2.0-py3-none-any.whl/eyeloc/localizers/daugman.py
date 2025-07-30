import cv2

import numpy as np

from ..localizers import Find
from ..prepocessing import image_preprocessing

class Daugman():
    def __init__(self, mode: int, preprocess: bool = True) -> None:
        assert mode in [Find.Pupil, Find.Iris], "Wrong mode value. Use one of: irisloc.FIND_PUPIL, irisloc.FIND_IRIS"
        self.mode = mode
        
        self.preprocess = preprocess
    
    def create_circle_mask(self, radius):
        mask = []
        for theta in np.linspace(0, 2 * np.pi, 128):
            a = int(radius * np.cos(theta))
            b = int(radius * np.sin(theta))
            mask.append((a, b, theta))
        return mask
    
    def compute_best_circle(self, grad_x, grad_y, height, width, radii_range):
        max_gradient_sum = 0
        best_circle = None

        for radius in radii_range:
            circle_mask = self.create_circle_mask(radius)
            for y in range(0, 127):
                for x in range(0, 127):
                    integral_sum = 0
                    count = 0

                    for point in circle_mask:
                        a = x + point[0]
                        b = y + point[1]

                        if 0 <= a < width and 0 <= b < height:
                            theta = point[2]
                            gradient = grad_x[b, a] * np.cos(theta) + grad_y[b, a] * np.sin(theta)
                            integral_sum += gradient
                            count += 1

                    if count > 0:
                        integral_sum /= count

                    if integral_sum > max_gradient_sum:
                        max_gradient_sum = integral_sum
                        best_circle = (x, y, radius)

        return best_circle

    def find(self, source):
        if self.preprocess:
            img = image_preprocessing(source)
        
        # Compute gradients using Sobel operator
        grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
        
        if self.mode == Find.Pupil:
            radii_range = range(8, 36, 1)
        elif self.mode == Find.Iris:
            radii_range = range(42, 64, 1)

        # Apply the Integro-differential operator using the optimized function
        height, width = img.shape
        best_circle = self.compute_best_circle(grad_x, grad_y, height, width, radii_range)

        return (best_circle[0], best_circle[1]), best_circle[2]
     