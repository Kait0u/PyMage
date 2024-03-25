import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os.path
from enum import Enum
import functools

from utils import cumsum

LMIN = 0
LMAX = 255


class ColorModes(Enum):
    RGB = "RGB"
    GRAY = "GRAY"
    LAB = "LAB"
    HSV = "HSV"


COLOR_CONVERSION_MODES = {
    ColorModes.RGB: {
        ColorModes.GRAY: cv.COLOR_RGB2GRAY,
        ColorModes.LAB: cv.COLOR_RGB2LAB,
        ColorModes.HSV: cv.COLOR_RGB2HSV
    },
    ColorModes.HSV: {
        ColorModes.RGB: cv.COLOR_HSV2RGB
    },
    ColorModes.LAB: {
        ColorModes.RGB: cv.COLOR_Lab2RGB
    },
    ColorModes.GRAY: {
        ColorModes.RGB: cv.COLOR_GRAY2RGB
    }
}


def grayscale_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.color_mode != ColorModes.GRAY:
            raise NotImplementedError("This operation can only be applied to grayscale images!")
        result = method(self, *args, **kwargs)
        return result

    return wrapper


def rgb_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.color_mode != ColorModes.RGB:
            raise NotImplementedError("This operation can only be applied to RGB images!")
        return method(self, *args, **kwargs)

    return wrapper


def hsv_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.color_mode != ColorModes.HSV:
            raise NotImplementedError("This operation can only be applied to HSV images!")
        return method(self, *args, **kwargs)

    return wrapper


def lab_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.color_mode != ColorModes.LAB:
            raise NotImplementedError("This operation can only be applied to LAB images!")
        return method(self, *args, **kwargs)

    return wrapper


def binary_only(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.color_mode != ColorModes.GRAY or not self.is_binary:
            raise NotImplementedError("This operation can only be applied to binary images!")
        return method(self, *args, **kwargs)

    return wrapper


class Image:
    def __init__(self, name: str, width: int, height: int, grayscale: bool = False):
        self._name = name
        self._width = width
        self._height = height
        self._img = np.zeros((height, width, 1 if grayscale else 3)) + LMAX  # Creates a width x height matrix of LMAX
        self._color_mode = ColorModes.GRAY if grayscale else ColorModes.RGB

        if self.color_mode == ColorModes.GRAY:
            self.create_histogram()

    @grayscale_only
    def create_histogram(self):
        self._histogram = Histogram(self)

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, value: np.ndarray):
        self._img = value.copy()
        if self.color_mode == ColorModes.GRAY:
            self.create_histogram()
        self._width = self._img.shape[1]
        self._height = self._img.shape[0]

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def histogram(self):
        return self._histogram

    @property
    def color_mode(self):
        return self._color_mode

    @staticmethod
    def from_file(path: str, grayscale: bool = False) -> "Image":
        img = cv.imread(path, cv.IMREAD_GRAYSCALE if grayscale else cv.IMREAD_COLOR)
        if not grayscale:
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        name = os.path.basename(path)
        width = img.shape[1]
        height = img.shape[0]

        new_image = Image(name, width, height, grayscale)
        new_image.img = img

        return new_image

    @staticmethod
    def from_numpy(arr: np.ndarray, name: str = None) -> "Image":
        width = arr.shape[1]
        height = arr.shape[0]
        grayscale = len(arr.shape) == 2 or arr.shape[2] == 1
        name = name if name is not None else "New"

        new_image = Image(name, width, height, grayscale)
        new_image.img = arr.copy()

        return new_image

    def copy(self) -> "Image":
        new_image = Image(self._name, self.width, self.height)
        new_image._color_mode = self.color_mode
        new_image.img = self._img.copy()

        return new_image

    def convert_color(self, to: ColorModes):
        curr_color = self.color_mode

        if curr_color != to:
            self._color_mode = to
            if len(COLOR_CONVERSION_MODES[curr_color].items()) > 1:
                self.img = cv.cvtColor(self.img, COLOR_CONVERSION_MODES[curr_color][to])
            elif to == ColorModes.RGB:
                self.img = cv.cvtColor(self.img, COLOR_CONVERSION_MODES[curr_color][to])
            else:
                self.img = cv.cvtColor(
                    cv.cvtColor(self.img, COLOR_CONVERSION_MODES[curr_color][ColorModes.RGB]),
                    COLOR_CONVERSION_MODES[ColorModes.RGB][to]
                )

    @property
    def is_gray(self):
        return self.color_mode == ColorModes.GRAY

    @property
    def is_binary(self):
        result = self.is_gray and np.unique(self.img) == np.array([LMIN, LMAX])
        return result

    def negate(self):
        self.img = LMAX - self.img

    @grayscale_only
    def stretch_histogram(self, new_min: int, new_max: int):
        curr_min = np.min(self.img)
        curr_max = np.max(self.img)

        def f(px): return int((px - curr_min) * new_max / (curr_max - curr_min))
        def stretch_f(px): return max(new_min, min(f(px), new_max))

        self.img = np.uint8(np.vectorize(stretch_f)(self.img))

    @grayscale_only
    def equalize_histogram(self):
        cs = cumsum(self.histogram.array)

        curr_min = np.min(cs)
        curr_max = np.max(cs)
        new_min = 0
        new_max = 255

        def f(px): return int((px - curr_min) * new_max / (curr_max - curr_min))
        def stretch_f(px): return max(new_min, min(f(px), new_max))

        cumsum_eq = np.uint8(np.vectorize(stretch_f)(cs))
        self.img = cumsum_eq[self.img]

    @rgb_only
    def split_rgb(self) -> tuple["Image", "Image", "Image"]:
        channels = [
            Image.from_numpy(
                self.img[:, :, idx].copy(),
                f"({['R', 'G', 'B'][idx]}) {self.name}"
            ) for idx in range(3)
        ]

        return tuple(channels)

    @lab_only
    def split_lab(self) -> tuple["Image", "Image", "Image"]:
        channels = [
            Image.from_numpy(
                self.img[:, :, idx].copy(),
                f"({['L', 'A', 'B'][idx]}) {self.name}"
            ) for idx in range(3)
        ]

        for channel in channels: channel.convert_color(ColorModes.GRAY)

        return tuple(channels)

    @hsv_only
    def split_hsv(self) -> tuple["Image", "Image", "Image"]:
        channels = [
            Image.from_numpy(
                self.img[:, :, idx].copy(),
                f"({['H', 'S', 'V'][idx]}) {self.name}"
            ) for idx in range(3)
        ]

        for channel in channels: channel.convert_color(ColorModes.GRAY)

        return tuple(channels)

    @grayscale_only
    def stretch_range(self, p1: int, p2: int, q3: int, q4: int):
        lut = np.arange(LMIN, LMAX + 1, 1, dtype=np.uint8)
        new_slice = np.floor(np.linspace(q3, q4, p2 - p1 + 1, True))
        lut[p1: p2 + 1] = new_slice

        self.apply_lut(lut)

    @grayscale_only
    def posterize(self, levels_of_grayness: int):
        length = LMAX - LMIN + 1
        bins = np.floor(np.linspace(LMIN, LMAX, levels_of_grayness, True)).astype(np.uint8)
        per_bin = LMAX // levels_of_grayness

        lut = []
        for idx in range(levels_of_grayness):
            lut += per_bin * [bins[idx]]

        while len(lut) < length:
            lut.append(bins[-1])

        lut = np.array(lut)
        self.apply_lut(lut)


    @grayscale_only
    def apply_lut(self, lut: np.ndarray):
        self.img = lut[self.img]

    def show(self):
        cv.imshow(self.name, self.img)
        cv.waitKey(0)


class Histogram:
    def __init__(self, image: Image, full_range: bool = True) -> None:
        if image.color_mode != ColorModes.GRAY:
            raise ValueError("Only gray images are supported for histogram!")
        self.parent = image
        self.histogramize(full_range)

    def histogramize(self, full_range: bool = True) -> None:
        self.full_range = full_range
        img_array = self.parent.img.flatten()
        if self.full_range:
            self.min = LMIN
            self.max = LMAX
            self.hist_array = np.arange(LMAX - LMIN + 1)
            self.hist_array = np.vectorize(lambda px: np.count_nonzero(img_array == px))(self.hist_array)
        else:
            self.min = np.min(img_array)
            self.max = np.max(img_array)
            self.hist_array = np.arange(self.min, self.max + 1)
            self.hist_array = np.vectorize(lambda px: np.count_nonzero(img_array == px))(self.hist_array)

    @property
    def array(self):
        return self.hist_array

    @property
    def array_normalized(self):
        max_val = self.hist_array.max()
        return self.array / max_val

    def show(self):
        x = np.arange(self.min, self.max + 1)
        y = self.hist_array

        plt.bar(x, y, color="black", align='center', width=1.0)
        plt.show()
