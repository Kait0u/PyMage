import cv2 as cv
import numpy as np


def moments(cnt: np.ndarray) -> dict[str, float]:
    mom = cv.moments(cnt)
    return mom


def area(cnt: np.ndarray) -> float:
    res_area = cv.contourArea(cnt)
    return res_area


def perimeter(cnt: np.ndarray) -> float:
    peri = cv.arcLength(cnt, True)
    return peri


def aspect_ratio(cnt: np.ndarray) -> float:
    x, y, w, h = cv.boundingRect(cnt)
    ar = float(w) / h
    return ar


def extent(cnt: np.ndarray) -> float:
    a = area(cnt)
    *_, w, h = cv.boundingRect(cnt)
    rect_area = w * h
    ext = float(a) / rect_area
    return ext


def solidity(cnt: np.ndarray) -> float:
    a = area(cnt)
    hull = cv.convexHull(cnt)
    hull_area = cv.contourArea(hull)
    soli = float(a) / hull_area
    return soli


def equivalent_diameter(cnt: np.ndarray) -> float:
    a = area(cnt)
    equi_diam = np.sqrt(4 * a / np.pi)
    return equi_diam
