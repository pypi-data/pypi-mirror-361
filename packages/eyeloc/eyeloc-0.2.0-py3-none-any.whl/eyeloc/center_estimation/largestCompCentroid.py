from numpy import uint8, argmax
from cv2 import threshold, equalizeHist, GaussianBlur, THRESH_BINARY_INV, connectedComponentsWithStats, CC_STAT_AREA
from ..localizers import autoScaleABC


def largestComponentCentroid(img):
    _, thr = threshold(equalizeHist(autoScaleABC(GaussianBlur(img, (3,3), 5)).astype(uint8)), 8, 255, THRESH_BINARY_INV)
    
    num_labels, labels, stats, centroids = connectedComponentsWithStats(thr, connectivity=8)

    # Определение наибольшей по площади области, исключая фон (первая метка)
    largest_label = 1 + argmax(stats[1:, CC_STAT_AREA])

    # Вычисление центроида наибольшей области
    return centroids[largest_label]