import numpy as np
from scipy.signal import convolve2d


def cumsum(arr: np.array) -> np.ndarray:
    csum = np.zeros_like(arr)
    csum[0] = arr[0]

    # idx will be moved to 0, so no subtraction needed
    # addition is needed instead
    for idx, val in enumerate(arr[1:]):
        csum[idx + 1] = csum[idx] + val

    return csum


def convolve_filters(f1: np.ndarray, f2: np.ndarray) -> np.ndarray:
    return convolve2d(f1, f2, mode="full")

