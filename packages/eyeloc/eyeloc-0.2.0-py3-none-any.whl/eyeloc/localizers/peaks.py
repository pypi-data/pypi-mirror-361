import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from cv2 import Canny

from .utils import delete_constant_tail, eye_func_half

from enum import Enum

class PolarPeaks(Enum):
    Gradient = 0
    FuncFitting = 1
    Canny = 2

def grad_peaks(polar, angles, mode_func):
    # Векторизованное вычисление градиентов для всех углов сразу
    selected_rows = polar[angles]
    derivatives = np.gradient(selected_rows, axis=1)
    derivatives = np.clip(derivatives, 0, None)
    
    peaks = []
    for i, deriv in enumerate(derivatives):
        maximas, _ = find_peaks(deriv)
        if len(maximas) > 2:
            ind_max = np.argpartition(deriv[maximas], -2)[-2:]
            peaks.append(mode_func(maximas[ind_max]))
        else:
            peaks.append(-1)
            
    return peaks

def canny_peaks(polar, angles, mode_func):
    # Применяем Canny один раз для всего изображения
    canny_polar = Canny(polar, 0, 255)
    selected_rows = canny_polar[angles]
    
    peaks = []
    for row in selected_rows:
        first_two = np.where(row > 0)[0][:2]
        if len(first_two) != 0:
            peaks.append(mode_func(first_two))
        else:
            peaks.append(-1)
        
    return peaks

def curvefit_peaks(polar, angles, mode_func):
    peaks = []
    r = 20
    for i, ang in enumerate(angles):
        values = delete_constant_tail(255-polar[ang])
        arguments = np.arange(0, len(values))
        center_im = values[0]
        
        popt, _ = curve_fit(eye_func_half, arguments, values,
                                p0=[r, center_im,
                                    0.7,
                                    2*r, r, 100,
                                    4.5*r, r, 0.1],
                                # bounds=([0.8*r, 0.8*center_im,
                                #             0,
                                #             r, 0, 0,
                                #             r, 0, -2],
                                #         [1.2*r, 1.2*center_im,
                                #         5,
                                #         192, 128, center_im,
                                #         192, 256, 2]),
                                # sigma=np.full(128, 1e-12),
                                method="trf",
                                maxfev=500000)
        
        if mode_func == np.max:
            peaks.append(popt[3]+popt[4]+1)
        elif mode_func == np.min:
            peaks.append(popt[0]+1)
            
    return peaks