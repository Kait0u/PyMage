# import cv2 as cv
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, qRgb
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QMenuBar, QAction, QWidget, QStatusBar

from image import Image, ColorModes
from histogram_window import HistogramWindow
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
        self.type_menu.addAction(to_grayscale_action)
        to_rgb_action = QAction("To RGB", self)
        to_rgb_action.triggered.connect(self.to_rgb)
        self.type_menu.addAction(to_rgb_action)
        self.type_menu.addSeparator()
        split_rgb_action = QAction("Split RGB", self)
        split_rgb_action.triggered.connect(self.split_rgb)
        self.type_menu.addAction(split_rgb_action)

        self.image_menu.addSeparator()
        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(self.duplicate)
        duplicate_action.setShortcut("Ctrl+D")
        self.image_menu.addAction(duplicate_action)

        self.image_menu.addSeparator()
        self.histogram_menu = self.image_menu.addMenu("&Histogram")

        equalize_action = QAction("Equalize", self)
        equalize_action.triggered.connect(self.equalize_histogram)
        self.histogram_menu.addAction(equalize_action)

        stretch_action = QAction("Stretch", self)
        stretch_action.triggered.connect(self.stretch_histogram)
        self.histogram_menu.addAction(stretch_action)

        self.histogram_menu.addSeparator()
        disp_hist_action = QAction("Display", self)
        disp_hist_action.setShortcut("Ctrl+H")
        disp_hist_action.triggered.connect(self.display_histogram)
        self.histogram_menu.addAction(disp_hist_action)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.image_frame = QLabel()
        self.layout.addWidget(self.image_frame)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.histogram_window = None
        self.refresh_image()

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
        color_format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

        self.qt_image = QImage(self.image.img, self.image.width,
                               self.image.height, self.image.img.strides[0], color_format)

        self.qt_image = QPixmap.fromImage(self.qt_image)
        self.image_frame.setPixmap(self.qt_image)
        self.image_frame.setAlignment(Qt.AlignCenter)

        histwin_exists = self.histogram_window is not None
        is_grayscale = self.image.is_gray

        if histwin_exists and is_grayscale:
            self.histogram_window.update_data()

        elif histwin_exists and not is_grayscale:
            WINDOW_MANAGER.remove_window(self.histogram_window)
            self.histogram_window = None

    def to_grayscale(self):
        self.image.convert_color(ColorModes.GRAY)
        self.refresh_image()

    def to_rgb(self):
        self.image.convert_color(ColorModes.RGB)
        self.refresh_image()

    def split_rgb(self):
        if not self.image.is_gray:
            imgs = self.image.split_channels()
            for img in imgs:
                img_win = ImageWindow(img)
                WINDOW_MANAGER.add_window(img_win)
                img_win.show()

        else:
            print("RGB only!")



    def duplicate(self):
        new_image = self.image.copy()
        new_image.name += "_duplicate"
        new_window = ImageWindow(new_image)
        WINDOW_MANAGER.add_window(new_window)
        new_window.show()

    def display_histogram(self):
        if self.image.is_gray:
            self.histogram_window = HistogramWindow(self)
            WINDOW_MANAGER.add_window(self.histogram_window)
            self.histogram_window.show()
        # else:
        #     raise NotImplementedError("No histogram window for this image!")

    def equalize_histogram(self):
        try:
            self.image.equalize_histogram()
            self.refresh_image()
        except NotImplementedError as error:
            print(error)

    def stretch_histogram(self):
        try:
            self.image.stretch_histogram(LMIN, LMAX)
            self.refresh_image()
        except NotImplementedError as error:
            print(error)
