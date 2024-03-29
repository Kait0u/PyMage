# import cv2 as cv
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QMenuBar, QAction, QWidget, QStatusBar

from forms.blur_form import BlurForm
from forms.canny_form import CannyForm
from forms.gblur_form import GBlurForm
from forms.laplasharpen_form import LaplaSharpenForm
from image import Image, ColorModes
from histogram_window import HistogramWindow
from forms.laplacian_form import LaplacianForm
from forms.posterize_form import PosterizeForm
from forms.range_stretch_form import RangeStretchForm
from forms.sobel_form import SobelForm
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
        split_rgb_action = QAction("Split as RGB", self)
        split_rgb_action.triggered.connect(self.split_rgb)
        self.type_menu.addAction(split_rgb_action)
        split_lab_action = QAction("Split as LAB", self)
        split_lab_action.triggered.connect(self.split_lab)
        self.type_menu.addAction(split_lab_action)
        split_hsv_action = QAction("Split as HSV", self)
        split_hsv_action.triggered.connect(self.split_hsv)
        self.type_menu.addAction(split_hsv_action)


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

        self.op_menu = self.menu_bar.addMenu("&Operations")
        self.unary_menu = self.op_menu.addMenu("&Unary")

        negate_action = QAction("Negate", self)
        negate_action.triggered.connect(self.negate)
        self.unary_menu.addAction(negate_action)

        stretch_range_action = QAction("Stretch range", self)
        stretch_range_action.triggered.connect(self.stretch_range)
        self.unary_menu.addAction(stretch_range_action)

        posterize_action = QAction("Posterize", self)
        posterize_action.triggered.connect(self.posterize)
        self.unary_menu.addAction(posterize_action)

        self.neighb_menu = self.op_menu.addMenu("&Neighborhood")

        blur_action = QAction("Blur", self)
        blur_action.triggered.connect(self.blur)
        self.neighb_menu.addAction(blur_action)

        gblur_action = QAction("Gaussian Blur", self)
        gblur_action.triggered.connect(self.gblur)
        self.neighb_menu.addAction(gblur_action)

        self.neighb_menu.addSeparator()

        canny_action = QAction("Canny", self)
        canny_action.triggered.connect(self.canny)
        self.neighb_menu.addAction(canny_action)

        laplacian_action = QAction("Laplacian", self)
        laplacian_action.triggered.connect(self.laplacian)
        self.neighb_menu.addAction(laplacian_action)

        sobel_action = QAction("Sobel", self)
        sobel_action.triggered.connect(self.sobel)
        self.neighb_menu.addAction(sobel_action)

        self.neighb_menu.addSeparator()

        laplasharpen_action = QAction("LaplaSharpen", self)
        laplasharpen_action.triggered.connect(self.laplasharpen)
        self.neighb_menu.addAction(laplasharpen_action)

        # Actual UI

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
        if self.histogram_window is not None:
            self.histogram_window.close()
        event.accept()
        WINDOW_MANAGER.remove_window(self)

    def check_gray(self):
        if not self.image.is_gray:
            raise Exception("Image is not a grayscale image")

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
        new_img = self.image.copy()
        new_img.convert_color(ColorModes.RGB)
        imgs = new_img.split_rgb()
        for img in imgs:
            img_win = ImageWindow(img)
            WINDOW_MANAGER.add_window(img_win)
            img_win.show()

    def split_lab(self):
        new_img = self.image.copy()
        new_img.convert_color(ColorModes.LAB)
        imgs = new_img.split_lab()
        for img in imgs:
            try: img.stretch_histogram(LMIN, LMAX)
            except: pass
            img_win = ImageWindow(img)
            WINDOW_MANAGER.add_window(img_win)
            img_win.show()

    def split_hsv(self):
        new_img = self.image.copy()
        new_img.convert_color(ColorModes.HSV)
        imgs = new_img.split_hsv()
        for img in imgs:
            try: img.stretch_histogram(LMIN, LMAX)
            except: pass
            img_win = ImageWindow(img)
            WINDOW_MANAGER.add_window(img_win)
            img_win.show()

    def duplicate(self):
        new_image = self.image.copy()
        new_image.name += "_duplicate"
        new_window = ImageWindow(new_image)
        WINDOW_MANAGER.add_window(new_window)
        new_window.show()

    def display_histogram(self):
        try:
            self.check_gray()
            self.histogram_window = HistogramWindow(self)
            WINDOW_MANAGER.add_window(self.histogram_window)
            self.histogram_window.show()
        except Exception as error:
            print(error)
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

    def negate(self):
        try:
            self.image.negate()
            self.refresh_image()
        except Exception as error:
            print(error)

    def stretch_range(self):
        try:
            result = RangeStretchForm.show_dialog(self)
            if result is None: return
            p1, p2, q3, q4 = result
            self.image.stretch_range(p1, p2, q3, q4)
            self.refresh_image()
        except Exception as error:
            print(error)

    def posterize(self):
        try:
            result = PosterizeForm.show_dialog(self)
            if result is None: return
            lvls = result
            self.image.posterize(lvls)
            self.refresh_image()
        except Exception as error:
            print(error)

    def blur(self):
        try:
            result = BlurForm.show_dialog(self)
            if result is None: return
            size = result
            self.image.blur(size)
            self.refresh_image()
        except Exception as error:
            print(error)

    def gblur(self):
        try:
            result = GBlurForm.show_dialog(self)
            if result is None: return
            kernel_size, sigma_x, sigma_y, padding = result
            self.image.gaussian_blur(kernel_size, sigma_x, sigma_y, padding)
            self.refresh_image()
        except Exception as error:
            print(error)

    def sobel(self):
        try:
            self.check_gray()
            result = SobelForm.show_dialog(self)
            if result is None: return
            kernel_size, ddepth, padding = result
            self.image.sobel(kernel_size, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            print(error)

    def laplacian(self):
        try:
            self.check_gray()
            result = LaplacianForm.show_dialog(self)
            if result is None: return
            kernel_size, ddepth, padding = result
            self.image.laplacian(kernel_size, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            print(error)

    def canny(self):
        try:
            self.check_gray()
            result = CannyForm.show_dialog(self)
            if result is None: return
            th1, th2 = result
            self.image.canny(th1, th2)
            self.refresh_image()
        except Exception as error:
            print(error)

    def laplasharpen(self):
        try:
            self.check_gray()
            result = LaplaSharpenForm.show_dialog(self)
            if result is None: return
            kernel, ddepth, padding = result
            self.image.convolve(kernel, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            print(error)

