import numpy as np
from scipy.optimize import leastsq


def fitCircleLS(points):
    x = points[:, 0]
    y = points[:, 1]
    
    def calcR(xc, yc):
        return np.sqrt((x-xc)**2 + (y-yc)**2)

    def f_2(center):
        Ri = calcR(*center)
        return Ri - Ri.mean()

    center_estimation = (x.mean(), y.mean())
    center, _ = leastsq(f_2, center_estimation)

    return center, calcR(*center).mean()