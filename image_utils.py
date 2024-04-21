import numpy as np
import cv2 as cv
from image import StructuringElementShape
from utils import rhombus_ones


def structuring_element(shape: StructuringElementShape, n: int):
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and at least 3")

    result = np.zeros((n, n))

    match shape:
        case StructuringElementShape.RECTANGLE:
            result = np.ones((n, n))
        case StructuringElementShape.CROSS:
            result = cv.getStructuringElement(cv.MORPH_CROSS, (n, n))
        case StructuringElementShape.ELLIPSE:
            result = cv.getStructuringElement(cv.MORPH_ELLIPSE, (n, n))
        case StructuringElementShape.RHOMBUS:
            result = rhombus_ones(n)

    return result

