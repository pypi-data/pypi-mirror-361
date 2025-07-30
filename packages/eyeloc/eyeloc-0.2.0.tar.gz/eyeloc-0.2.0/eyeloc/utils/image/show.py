import cv2
import numpy as np
import matplotlib.pyplot as plt


def imshow(image):
    if len(image.shape) == 2:
        plt.imshow(image, cmap='gray', vmin=0, vmax=255)
    elif len(image.shape) == 3:
        plt.imshow(image, vmin=0, vmax=255)
    plt.show()

def show_circle(image, center, radius, color = (0, 255, 0)):
    if len(image.shape) == 2:
        img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR).astype(np.uint8)
    elif len(image.shape) == 3:
        img = image.copy().astype(np.uint8)
        
    cv2.circle(img, np.round(center).astype(int), round(radius), color)
    
    plt.imshow(img, vmin=0, vmax=255)
    plt.show()
    
def show_circles(image, centers, radiuses, colors: list = None):
    if len(image.shape) == 2:
        img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR).astype(np.uint8)
    elif len(image.shape) == 3:
        img = image.copy().astype(np.uint8)
        
    if colors == None:
        colors = [(0, 255, 0)] * len(centers)
        
    for center, radius, color in zip(centers, radiuses, colors):
        cv2.circle(img, np.round(center).astype(int), round(radius), color)
    
    plt.imshow(img, vmin=0, vmax=255)
    plt.show()