from enum import Enum

class CenterEstimation(Enum):
    Min = 0
    LargestComponentCentroid = 1
    # TODO Add more center estimation methods

from .darkestPixel import *
from .largestCompCentroid import *