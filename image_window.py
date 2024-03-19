# import cv2 as cv
import functools

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, qRgb
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QMenuBar, QAction, QWidget

from image import Image, ColorModes

from window_manager import WINDOW_MANAGER

LMIN = 0
LMAX = 255
SCALING = [25, 50, 100, 150, 200]


class ImageWindow(QMainWindow):
    def __init__(self, image: Image):
        super().__init__()
        self.image = image

        self.setWindowTitle(self.image.name)
        # self.resize(self.image.width, self.image.height)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.image_menu = self.menu_bar.addMenu("&Image")

        self.type_menu = self.image_menu.addMenu("&Type")
        to_grayscale_action = QAction("To Grayscale (8b)", self)
        to_grayscale_action.triggered.connect(self.to_grayscale)
        to_rgb_action = QAction("To RGB", self)
        to_rgb_action.triggered.connect(self.to_rgb)
        self.type_menu.addAction(to_grayscale_action)
        self.type_menu.addAction(to_rgb_action)

        self.image_menu.addSeparator()
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(self.duplicate)
        duplicate_action.setShortcut("Ctrl+D")
        self.image_menu.addAction(duplicate_action)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.image_frame = QLabel()
        self.layout.addWidget(self.image_frame)

        format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

        self.qt_image = QImage(self.image.img, self.image.width,
                               self.image.height, self.image.img.strides[0], format)

        self.qt_image = QPixmap.fromImage(self.qt_image)
        self.image_frame.setPixmap(self.qt_image)
        self.image_frame.setAlignment(Qt.AlignCenter)

    @staticmethod
    def from_path(path: str, grayscale: bool = False) -> "ImageWindow":
        new_image = Image.from_file(path, grayscale)
        new_window = ImageWindow(new_image)

        return new_window

    @staticmethod
    def from_numpy(arr: np.ndarray, name: str) -> "ImageWindow":
        new_image = Image.from_numpy(arr.copy(), name)
        new_window = ImageWindow(new_image)

        return new_window

    def closeEvent(self, event):
        event.accept()
        WINDOW_MANAGER.remove_window(self)

    def refresh_image(self):
        format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

        self.qt_image = QImage(self.image.img, self.image.width,
                               self.image.height, self.image.img.strides[0], format)

        self.qt_image = QPixmap.fromImage(self.qt_image)
        self.image_frame.setPixmap(self.qt_image)
        self.image_frame.setAlignment(Qt.AlignCenter)

    def to_grayscale(self):
        self.image.convert_color(ColorModes.GRAY)
        self.refresh_image()

    def to_rgb(self):
        self.image.convert_color(ColorModes.RGB)
        self.refresh_image()

    def duplicate(self):
        new_image = self.image.copy()
        new_image.name += "_duplicate"
        new_window = ImageWindow(new_image)
        WINDOW_MANAGER.add_window(new_window)
        new_window.show()

