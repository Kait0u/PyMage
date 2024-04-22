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


class Padding(Enum):
    REFLECT = cv.BORDER_REFLECT
    ISOLATED = cv.BORDER_ISOLATED
    REPLICATE = cv.BORDER_REPLICATE


class DesiredDepth(Enum):
    U8 = cv.CV_8U
    F64 = cv.CV_64F


class StructuringElementShape(Enum):
    ELLIPSE = "ELLIPSE"
    RECTANGLE = "RECTANGLE"
    CROSS = "CROSS"
    RHOMBUS = "RHOMBUS"


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
        result = self.is_gray and (np.array_equal(np.unique(self.img), np.array([LMIN, LMAX]))
                                   or np.array_equal(np.unique(self.img), np.array([LMIN]))
                                   or np.array_equal(np.unique(self.img), np.array([LMAX])))
        return result

    @property
    def is_black(self):
        return self.is_gray and np.array_equal(np.unique(self.img), np.array([LMIN]))

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

    def blur(self, kernel_size: int):
        self.img = cv.blur(self.img, (kernel_size, kernel_size))

    def gaussian_blur(self, kernel_size: int, sigma_x: float, sigma_y: float | None, padding: Padding):
        if sigma_y is None: sigma_y = sigma_x
        ksize = (kernel_size, kernel_size)
        self.img = cv.GaussianBlur(self.img, ksize=ksize, sigmaX=sigma_x, sigmaY=sigma_y, borderType=padding.value)

    @grayscale_only
    def laplacian(self, kernel_size: int, ddepth: DesiredDepth, padding: Padding):
        self.img = cv.Laplacian(self.img, ddepth=ddepth.value, ksize=kernel_size, borderType=padding.value)

    @grayscale_only
    def sobel(self, kernel_size: int, ddepth: DesiredDepth, padding: Padding):
        sobel_x = cv.Sobel(self.img, ddepth.value, dx=1, dy=0, ksize=kernel_size, borderType=padding.value)
        sobel_y = cv.Sobel(self.img, ddepth.value, dx=0, dy=1, ksize=kernel_size, borderType=padding.value)
        self.img = cv.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)

    @grayscale_only
    def canny(self, threshold1: int, threshold2: int):
        self.img = cv.Canny(self.img, threshold1, threshold2)

    @grayscale_only
    def convolve(self, kernel: np.ndarray, ddepth: DesiredDepth, padding: Padding, normalize: bool = True):
        normalizer = max(kernel.sum(), 1) if normalize else 1
        self.img = cv.filter2D(self.img, ddepth.value, kernel / normalizer, borderType=padding.value)

    def median(self, size: int, padding: Padding):
        if not (size > 1 and size % 2 == 1):
            raise ValueError("Invalid size!")
        padding_size = (size - 1) // 2
        temp = cv.copyMakeBorder(self.img,
                                 top=padding_size,
                                 bottom=padding_size,
                                 left=padding_size,
                                 right=padding_size,
                                 borderType=padding.value)
        temp = cv.medianBlur(temp, size)
        self.img = temp[padding_size:-padding_size, padding_size:-padding_size]

    def show(self):
        cv.imshow(self.name, self.img)
        cv.waitKey(0)

    @staticmethod
    def add_images(img1: "Image", img2: "Image", name: str | None) -> "Image":
        im1 = img1.img
        im2 = img2.img
        result = cv.add(im1, im2)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @staticmethod
    def subtract_images(img1: "Image", img2: "Image", name: str | None) -> "Image":
        im1 = img1.img
        im2 = img2.img
        result = cv.subtract(im1, im2)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @staticmethod
    def blend_images(img1: "Image", alpha: float, img2: "Image", beta: float, gamma: int, name: str | None) -> "Image":
        im1 = img1.img
        im2 = img2.img
        result = cv.addWeighted(im1, alpha, im2, beta, gamma)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @staticmethod
    def bitwise_and_images(img1: "Image", img2: "Image", name: str | None) -> "Image":
        im1 = img1.img
        im2 = img2.img
        result = cv.bitwise_and(im1, im2)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @staticmethod
    def bitwise_or_images(img1: "Image", img2: "Image", name: str | None) -> "Image":
        im1 = img1.img
        im2 = img2.img
        result = cv.bitwise_or(im1, im2)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @staticmethod
    def bitwise_xor_images(img1: "Image", img2: "Image", name: str | None) -> "Image":
        im1 = img1.img
        im2 = img2.img
        result = cv.bitwise_xor(im1, im2)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @staticmethod
    def bitwise_not_image(img1: "Image", name: str | None) -> "Image":
        im1 = img1.img
        result = cv.bitwise_not(im1)
        result_name = name if name is not None else "Untitled"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    def bitwise_not(self):
        result = cv.bitwise_not(self.img)
        result_name = f"not_{self.name}"
        result_image = Image.from_numpy(result, result_name)
        return result_image

    @binary_only
    def dilate(self, kernel: np.array, padding: Padding, anchor: tuple[int, int] = (-1, -1)):
        self.img = cv.dilate(self.img, kernel, anchor=anchor, borderType=padding.value)

    @binary_only
    def erode(self, kernel: np.array, padding: Padding, anchor: tuple[int, int] = (-1, -1)):
        self.img = cv.erode(self.img, kernel, anchor=anchor, borderType=padding.value)

    @binary_only
    def morph_open(self, kernel: np.array, padding: Padding, anchor: tuple[int, int] = (-1, -1)):
        self.erode(kernel, padding, anchor=anchor)
        self.dilate(kernel, padding, anchor=anchor)

    @binary_only
    def morph_close(self, kernel: np.array, padding: Padding, anchor: tuple[int, int] = (-1, -1)):
        self.dilate(kernel, padding, anchor=anchor)
        self.erode(kernel, padding, anchor=anchor)

    @binary_only
    def skeletonize(self, kernel: np.array, padding: Padding, anchor: tuple[int, int] = (-1, -1)):
        skel = np.zeros_like(self.img)
        img_copy = self.img.copy()
        kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))

        while True:
            img_open = cv.erode(img_copy, kernel, anchor=anchor, borderType=padding.value)
            img_open = cv.dilate(img_open, kernel, anchor=anchor, borderType=padding.value)
            img_subtr = cv.subtract(img_copy, img_open)
            img_er = cv.erode(img_copy, kernel, anchor=anchor, borderType=padding.value)
            skel = cv.bitwise_or(skel, img_subtr)
            img_copy = img_er.copy()
            if cv.countNonZero(img_copy) == 0:
                self.img = skel
                break

    @grayscale_only
    def hough(self, rho, theta, threshold) -> "Image":
        edges = cv.Canny(self.img, 50, 150)
        lines = cv.HoughLines(edges, rho, theta, threshold)
        if lines is None:
            raise ValueError("Nothing has been detected...")
        img_copy = np.repeat(self.img[..., np.newaxis], 3, axis=2)
        thickness = 2
        color = (0, 0, 255)
        length = (max(self.img.shape) // 1000 + 1) * 1000
        for line in lines:
            for rho_local, theta_local in line:
                a = np.cos(theta_local)
                b = np.sin(theta_local)
                x0 = a * rho_local
                y0 = b * rho_local
                pt1 = (int(x0 + length * (-b)), int(y0 + length * a))
                pt2 = (int(x0 - length * (-b)), int(y0 - length * a))
                cv.line(img_copy, pt1, pt2, color, thickness, cv.LINE_AA)

        result = Image.from_numpy(img_copy, f"hough_{self.name}")
        return result

    def pyramid(self, skip_quarter=False, skip_half=False, skip_double=False, skip_quadruple=False) -> list["Image"]:
        results = []
        w, h = map(int, self.img.shape[:2])
        if not skip_quarter:
            temp = cv.pyrDown(self.img)
            temp = cv.pyrDown(temp)
            results.append(Image.from_numpy(temp, f"25%_{self.name}"))
        if not skip_half:
            temp = cv.pyrDown(self.img)
            results.append(Image.from_numpy(temp, f"50%_{self.name}"))
        if not skip_double:
            temp = cv.pyrUp(self.img)
            results.append(Image.from_numpy(temp, f"200%_{self.name}"))
        if not skip_quadruple:
            temp = cv.pyrUp(self.img)
            temp = cv.pyrUp(temp)
            results.append(Image.from_numpy(temp, f"400%_{self.name}"))

        return results


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
