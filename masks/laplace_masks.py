import numpy as np
from enum import Enum


class LaplaSharpen(Enum):
    CROSS_5 = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0],
    ]

    SQUARE_5 = [
        [1, -2, 1],
        [-2, -5, -2],
        [1, -2, 1]
    ]

    SQUARE_9 = [
        [-1, -1, -1],
        [-1, 9, -1],
        [-1, -1, -1]
    ]

    @property
    def value(self):
        return np.array(self._value_)


