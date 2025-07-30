from cv2 import imread, IMREAD_GRAYSCALE

def eyeimread(filename: str):
    image = imread(filename, IMREAD_GRAYSCALE)
    return image[:, :image.shape[1]//2], image[:, image.shape[1]//2:]