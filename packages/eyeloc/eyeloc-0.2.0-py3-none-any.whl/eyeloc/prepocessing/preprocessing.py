import cv2
import numpy as np
from functools import lru_cache

from ..localizers import sharpen, autoScaleABC

def equalizeHistInverse(image):
    # Расчет гистограммы и CDF
    hist, _ = np.histogram(cv2.GaussianBlur(image, (15, 15), 10).flatten(), 256, [0, 256])
    cdf = hist.cumsum()
    cdf_normalized = (cdf - cdf.min()) * 255 / (cdf.max() - cdf.min())
    lookup_table = np.uint8(cdf_normalized)  # Таблица преобразования

    # Создаем пары (v, s), где v = lookup_table[s], и удаляем дубликаты v
    pairs = [(v, s) for s, v in enumerate(lookup_table)]
    unique_pairs = {}
    for v, s in pairs:
        unique_pairs[v] = s  # Сохраняем последнее s для каждого v (как в оригинале)
    v_values = np.array(list(unique_pairs.keys()))
    s_values = np.array(list(unique_pairs.values()))

    # Сортируем пары по v для интерполяции
    sort_idx = np.argsort(v_values)
    v_sorted = v_values[sort_idx]
    s_sorted = s_values[sort_idx]

    # Создаем интерполированную обратную таблицу для всех v [0, 255]
    all_v = np.arange(256)
    # Линейная интерполяция s по v
    interpolated_s = np.interp(all_v, v_sorted, s_sorted)
    inverse_lookup = np.uint8(interpolated_s)

    # Применяем обратное преобразование с интерполяцией
    return cv2.LUT(image, inverse_lookup)

@lru_cache(maxsize=32)
def _get_structuring_element(morph_struct_element, size):
    """Кэшируем структурные элементы для морфологических операций"""
    return cv2.getStructuringElement(morph_struct_element, (size, size))

def image_preprocessing(source, sharpen_weight = 1, sharpen_gauss_ksize = 3, sharpen_gamma_sigmaX = 1,
                        morph_struct_element = cv2.MORPH_CROSS, morph_blur_size = 9, morph_operations = [cv2.MORPH_OPEN], morph_iterations = [1],
                        median_blur_ksize = 9):
    if len(source.shape) == 3:
        img = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    elif  len(source.shape) == 2:
        img = source.copy().astype(np.uint8)
    
    # INPAINTING DATA IN IMAGE
    inp_mask = np.zeros(img.shape, dtype=np.uint8)
    inp_mask[0, :19] = 1
    
    inp = cv2.inpaint(img, inp_mask, 1, cv2.INPAINT_TELEA)
    
    img = cv2.medianBlur(inp, median_blur_ksize)
    
    # img = equalizeHistInverse(inp)
    
    # SHARPENING
    img = sharpen(img, weight = sharpen_weight, gauss_ksize = sharpen_gauss_ksize, gauss_sigmaX = sharpen_gamma_sigmaX)
    
    # Предварительно получаем структурный элемент
    kernel = _get_structuring_element(morph_struct_element, morph_blur_size)
    
    # BLURING - используем предвычисленный kernel
    for operation, iterations in zip(morph_operations, morph_iterations):
        img = cv2.morphologyEx(img, operation, kernel, iterations=iterations)
    
    img = autoScaleABC(img)
    return img, inp
