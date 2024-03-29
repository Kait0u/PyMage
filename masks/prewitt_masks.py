import numpy as np
from enum import Enum

# Source: https://documentation.help/NI-Vision-Visual-Basic/kernels.html

class Prewitt(Enum):
    N = [
        [-1, -1, -1],
        [0, 0, 0],
        [1, 1, 1],
    ]

    NE = [
        [0, -1, -1],
        [1, 0, -1],
        [1, 1, 0]
    ]

    E = [
        [1, 0, -1],
        [1, 0, -1],
        [1, 0, -1]
    ]

    SE = [
        [1, 1, 0],
        [1, 0, -1],
        [0, -1, -1]
    ]

    S = [
        [1, 1, 1],
        [0, 0, 0],
        [-1, -1, -1]
    ]

    SW = [
        [0, 1, 1],
        [-1, 0, 1],
        [-1, -1, 0]
    ]

    W = [
        [-1, 0, 1],
        [-1, 0, 1],
        [-1, 0, 1]
    ]

    NW = [
        [-1, -1, 0],
        [-1, 0, 1],
        [0, 1, 1]
    ]

    @property
    def value(self):
        return np.array(self._value_)
