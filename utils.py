from typing import List, Tuple

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


def _bresenham_low(x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    result = []
    dx = x2 - x1
    dy = y2 - y1
    yi = 1
    if dy < 0:
        yi = -1
        dy = -dy
    d = 2 * dy - dx
    y = y1

    for x in range(x1, x2 + 1):
        result.append((x, y))
        if d > 0:
            y += yi
            d += 2 * (dy - dx)
        else:
            d += 2 * dy

    return np.array(result)


def _bresenham_high(x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    result = []
    dx = x2 - x1
    dy = y2 - y1
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    d = 2 * dx - dy
    x = x1

    for y in range(y1, y2 + 1):
        result.append((x, y))
        if d > 0:
            x += xi
            d += 2 * (dx - dy)
        else:
            d += 2 * dx

    return np.array(result)


def bresenham(x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    if abs(y2 - y1) < abs(x2 - x1):
        if x1 > x2:
            return _bresenham_low(x2, y2, x1, y1)
        else:
            return _bresenham_low(x1, y1, x2, y2)
    else:
        if y1 > y2:
            return _bresenham_high(x2, y2, x1, y1)
        else:
            return _bresenham_high(x1, y1, x2, y2)


def rhombus_ones(n: int) -> np.ndarray:
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and at least 3")

    result = np.zeros((n, n))
    center = n // 2

    for level in range(0, center + 1):
        result[level, center - level: center + level + 1] = 1
        if level != center: result[n - level - 1, center - level: center + level + 1] = 1

    return result



