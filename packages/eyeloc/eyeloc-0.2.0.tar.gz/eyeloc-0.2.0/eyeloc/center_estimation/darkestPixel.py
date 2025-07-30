from numpy import round, unravel_index, argmin, uint8

def darkestPixel(img):
    return round(unravel_index(argmin(img), shape=img.shape))[::-1].astype(uint8)