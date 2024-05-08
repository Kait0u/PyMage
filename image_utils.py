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


def make_binary_rle(rle: list[tuple[int, int]], height: int, width: int) -> bytearray:
    header_structure = (4, 4)
    entry_structure = (2, 4)

    rle_bytes = bytearray()

    header_vals = (height, width)
    for idx, val in enumerate(header_vals):
        v = int(val)
        b = v.to_bytes(header_structure[idx], "big")
        rle_bytes.extend(b)

    for pair in rle:
        for idx, val in enumerate(pair):
            v = int(val)
            b = v.to_bytes(entry_structure[idx], "big")
            rle_bytes.extend(b)

    return rle_bytes


def parse_binary_rle(input_bytes: bytearray) -> np.ndarray:
    header_structure = (4, 4)
    entry_structure = (2, 4)

    temp_bytes = input_bytes.copy()

    height = int.from_bytes(temp_bytes[:header_structure[0]], byteorder="big")
    del temp_bytes[:header_structure[0]]

    width = int.from_bytes(temp_bytes[:entry_structure[1]], byteorder="big")
    del temp_bytes[:entry_structure[1]]

    result = np.zeros(height * width, dtype=np.uint8)
    filled = 0

    while temp_bytes:
        entry_bytes = []
        for length in entry_structure:
            b = temp_bytes[:length]
            entry_bytes.append(b)
            del temp_bytes[:length]

        # There are two items in that list

        pixel_value_b, pixel_count_b = entry_bytes
        pixel_value = int.from_bytes(pixel_value_b, byteorder="big")
        pixel_count = int.from_bytes(pixel_count_b, byteorder="big")

        result[filled: filled + pixel_count] = pixel_value
        filled += pixel_count

    result = result.reshape((height, width))
    return result