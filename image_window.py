import os

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPalette
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QMenuBar, QAction, QWidget, QStatusBar, QMessageBox, \
    QFileDialog

from error_box import ErrorBox
from histogram_window import HistogramWindow
from image import Image, ColorModes
from image_utils import structuring_element
from info_box import InfoBox
from object_traits_window import ObjectTraitsWindow
from utils import bresenham
from widgets.scale_slider import ScaleSlider
from window_manager import WINDOW_MANAGER

LMIN = 0
LMAX = 255


class ImageWindow(QMainWindow):
    def __init__(self, image: Image):
        super().__init__()
        WINDOW_MANAGER.add_window(self)
        self.id = WINDOW_MANAGER.generate_uid(self)

        self.image = image
        self.current_zoom = 100
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        self.setWindowTitle(f"{self.image.name} ({self.id}) | PyMage")
        self.setWindowIcon(QIcon("assets/icon.png"))

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.image_frame = QLabel()
        self.layout.addWidget(self.image_frame)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)


        # [Menu bar]

        # Image
        self.image_menu = self.menu_bar.addMenu("&Image")

        # Type
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

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save)
        self.image_menu.addAction(save_action)

        save_rle_action = QAction("Save (RLE)", self)
        save_rle_action.triggered.connect(self.save_rle)
        self.image_menu.addAction(save_rle_action)

        duplicate_action = QAction("Duplicate", self)
        duplicate_action.triggered.connect(self.duplicate)
        duplicate_action.setShortcut("Ctrl+D")
        self.image_menu.addAction(duplicate_action)

        self.image_menu.addSeparator()

        # Histogram submenu
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

        self.image_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.quit)
        self.image_menu.addAction(quit_action)

        # Operations
        self.op_menu = self.menu_bar.addMenu("&Operations")

        # Unary submenu
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

        # Neighborhood submenu
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

        prewitt_action = QAction("Prewitt", self)
        prewitt_action.triggered.connect(self.prewitt)
        self.neighb_menu.addAction(prewitt_action)

        self.neighb_menu.addSeparator()

        laplasharpen_action = QAction("LaplaSharpen", self)
        laplasharpen_action.triggered.connect(self.laplasharpen)
        self.neighb_menu.addAction(laplasharpen_action)

        self.neighb_menu.addSeparator()

        median_action = QAction("Median", self)
        median_action.triggered.connect(self.median)
        self.neighb_menu.addAction(median_action)

        self.neighb_menu.addSeparator()

        convolve_action = QAction("Convolve", self)
        convolve_action.triggered.connect(self.convolve)
        self.neighb_menu.addAction(convolve_action)

        two_stage_filter_action = QAction("Two Stage Filter", self)
        two_stage_filter_action.triggered.connect(self.two_stage_filter)
        self.neighb_menu.addAction(two_stage_filter_action)

        # Arithmetic

        self.arithmetic_menu = self.menu_bar.addMenu("&Arithmetic")

        add_action = QAction("Add", self)
        add_action.triggered.connect(self.add_image)
        self.arithmetic_menu.addAction(add_action)

        sub_action = QAction("Subtract", self)
        sub_action.triggered.connect(self.subtract_image)
        self.arithmetic_menu.addAction(sub_action)

        blend_action = QAction("Blend", self)
        blend_action.triggered.connect(self.blend_image)
        self.arithmetic_menu.addAction(blend_action)

        self.arithmetic_menu.addSeparator()

        and_action = QAction("AND", self)
        and_action.triggered.connect(self.bitwise_and_image)
        self.arithmetic_menu.addAction(and_action)

        or_action = QAction("OR", self)
        or_action.triggered.connect(self.bitwise_or_image)
        self.arithmetic_menu.addAction(or_action)

        xor_action = QAction("XOR", self)
        xor_action.triggered.connect(self.bitwise_xor_image)
        self.arithmetic_menu.addAction(xor_action)

        not_action = QAction("NOT", self)
        not_action.triggered.connect(self.bitwise_not_image)
        self.arithmetic_menu.addAction(not_action)

        # Morphology

        self.morphology_menu = self.menu_bar.addMenu("&Morphology")

        erosion_action = QAction("Erosion", self)
        erosion_action.triggered.connect(self.erode)
        self.morphology_menu.addAction(erosion_action)

        dilation_action = QAction("Dilation", self)
        dilation_action.triggered.connect(self.dilate)
        self.morphology_menu.addAction(dilation_action)

        opening_action = QAction("Opening", self)
        opening_action.triggered.connect(self.morph_open)
        self.morphology_menu.addAction(opening_action)

        closing_action = QAction("Closing", self)
        closing_action.triggered.connect(self.morph_close)
        self.morphology_menu.addAction(closing_action)

        self.morphology_menu.addSeparator()

        skeletonization_action = QAction("Skeletonization", self)
        skeletonization_action.triggered.connect(self.skeletonize)
        self.morphology_menu.addAction(skeletonization_action)

        # Analysis
        self.analysis_menu = self.menu_bar.addMenu("&Analysis")

        hough_action = QAction("Hough", self)
        hough_action.triggered.connect(self.hough)
        self.analysis_menu.addAction(hough_action)

        profile_action = QAction("Profile Line", self)
        profile_action.triggered.connect(self.profile_line)
        self.analysis_menu.addAction(profile_action)

        pyramid_action = QAction("Image Pyramid", self)
        pyramid_action.triggered.connect(self.pyramid)
        self.analysis_menu.addAction(pyramid_action)

        self.analysis_menu.addSeparator()

        # Segmentation submenu
        self.segmentation_menu = self.analysis_menu.addMenu("&Segmentation")

        thresholding_action = QAction("Thresholding", self)
        thresholding_action.triggered.connect(self.thresholding)
        self.segmentation_menu.addAction(thresholding_action)

        adaptive_thresholding_action = QAction("Adaptive Thresholding", self)
        adaptive_thresholding_action.triggered.connect(self.adaptive_thresholding)
        self.segmentation_menu.addAction(adaptive_thresholding_action)

        otsu_thresholding_action = QAction("Otsu Thresholding", self)
        otsu_thresholding_action.triggered.connect(self.otsu_thresholding)
        self.segmentation_menu.addAction(otsu_thresholding_action)

        self.segmentation_menu.addSeparator()

        grabcut_rect_action = QAction("GrabCut (Rect)", self)
        grabcut_rect_action.triggered.connect(self.grabcut_rect)
        self.segmentation_menu.addAction(grabcut_rect_action)

        grabcut_mask_action = QAction("GrabCut (Mask)", self)
        grabcut_mask_action.triggered.connect(self.grabcut_mask)
        self.segmentation_menu.addAction(grabcut_mask_action)

        self.segmentation_menu.addSeparator()

        watershed_action = QAction("Watershed", self)
        watershed_action.triggered.connect(self.watershed)
        self.segmentation_menu.addAction(watershed_action)

        # -----------------------------

        self.analysis_menu.addSeparator()

        inpainting_action = QAction("Inpaint", self)
        inpainting_action.triggered.connect(self.inpaint)
        self.analysis_menu.addAction(inpainting_action)

        self.analysis_menu.addSeparator()

        contours_action = QAction("Colorful Contours", self)
        contours_action.triggered.connect(self.colorful_contours)
        self.analysis_menu.addAction(contours_action)

        traits_action = QAction("Object Traits", self)
        traits_action.triggered.connect(self.object_traits)
        self.analysis_menu.addAction(traits_action)

        # [Status bar]
        self.status_bar.setSizeGripEnabled(False)

        self.color_status_label = QLabel()
        self.color_status_label.setContentsMargins(10, 0, 10, 0)
        self.status_bar.addWidget(self.color_status_label)

        self.scale_slider = ScaleSlider()
        self.scale_slider.valueChanged.connect(self.slider_changed)
        self.status_bar.addPermanentWidget(self.scale_slider)

        # [Post-render activities]

        bgc = self.palette().color(self.backgroundRole()).getRgb()[:3]  # Background color
        tc = self.palette().color(QPalette.WindowText).getRgb()[:3]  # Text color

        self.status_bar.setStyleSheet("""
        QStatusBar {
            border-left: 1px inset #AAAAAA;
            border-top: 1px inset #AAAAAA;
        """ +
        f"""
            background: rgb{bgc};
        """ +
        """
        }
        
        QStatusBar QLabel {
        """ +
        f"""
        color: rgb{tc};
        """ +
        """
        }
        """)

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

    def __str__(self):
        return f"{self.image.name} [{self.id}]"

    def check_gray(self):
        if not self.image.is_gray:
            raise Exception("Image is not a grayscale image")

    def check_binary(self):
        if not self.image.is_binary:
            raise Exception("Image is not a binary image")

    def update_color_status(self):
        if self.image.is_binary:
            self.color_status_label.setText("GRAY (BIN)")
        elif self.image.is_gray:
            self.color_status_label.setText("GRAY")
        else:
            self.color_status_label.setText("RGB")

    def refresh_image(self):
        self.update_preview(self.current_zoom)

        self.update_color_status()

        histwin_exists = self.histogram_window is not None
        is_grayscale = self.image.is_gray

        if histwin_exists and is_grayscale:
            self.histogram_window.update_data()

        elif histwin_exists and not is_grayscale:
            WINDOW_MANAGER.remove_window(self.histogram_window)
            self.histogram_window = None

    def slider_changed(self, value):
        percent = self.scale_slider.value
        self.current_zoom = percent
        self.update_preview(percent)

    def update_preview(self, scale_percent: int):
        try:
            w = self.image.width
            h = self.image.height

            if scale_percent != 100:
                new_w = int(w / 100 * scale_percent)
                new_h = int(h / 100 * scale_percent)
            else:
                new_w = w
                new_h = h

            color_format = QImage.Format_RGB888 if not self.image.is_gray else QImage.Format_Grayscale8
            self.qt_image = QImage(self.image.img, self.image.width,
                                   self.image.height, self.image.img.strides[0], color_format)
            self.qt_image = QPixmap.fromImage(self.qt_image)
            self.qt_image = self.qt_image.scaled(new_w, new_h)
            self.image_frame.setPixmap(self.qt_image)
            self.image_frame.setAlignment(Qt.AlignCenter)

            size = self.qt_image.size()
            self.widget.setMinimumSize(size)
            self.adjust_size()

        except Exception as error:
            ErrorBox(error)

    def adjust_size(self):
        was_maximized = self.isMaximized()

        self.showNormal()

        self.image_frame.adjustSize()
        self.widget.adjustSize()
        self.adjustSize()

        if was_maximized:
            self.showMaximized()

    def quit(self):
        confirmation_box = QMessageBox
        answer = confirmation_box.question(self,
                                           "Quit", "Are you sure you want to quit?\nUnsaved changes will be lost!",
                                           confirmation_box.Yes | confirmation_box.No
                                           )
        if answer == confirmation_box.Yes:
            self.close()

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
            try:
                img.stretch_histogram(LMIN, LMAX)
            except ValueError as error:
                pass
            except Exception as error:
                ErrorBox(error)
            img_win = ImageWindow(img)
            WINDOW_MANAGER.add_window(img_win)
            img_win.show()

    def split_hsv(self):
        new_img = self.image.copy()
        new_img.convert_color(ColorModes.HSV)
        imgs = new_img.split_hsv()
        for img in imgs:
            try:
                img.stretch_histogram(LMIN, LMAX)
            except ValueError as error:
                pass
            except Exception as error:
                ErrorBox(error)
            img_win = ImageWindow(img)
            WINDOW_MANAGER.add_window(img_win)
            img_win.show()

    def duplicate(self):
        new_image = self.image.copy()
        new_image.name = f"dup_{new_image.name}"
        new_window = ImageWindow(new_image)
        new_window.show()

    def display_histogram(self):
        try:
            self.check_gray()
            self.histogram_window = HistogramWindow(self)
            self.histogram_window.show()
        except Exception as error:
            ErrorBox(error)

    def equalize_histogram(self):
        try:
            self.check_gray()
            self.image.equalize_histogram()
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def stretch_histogram(self):
        try:
            self.check_gray()
            self.image.stretch_histogram(LMIN, LMAX)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def negate(self):
        try:
            self.image.negate()
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def stretch_range(self):
        from forms.range_stretch_form import RangeStretchForm

        try:
            self.check_gray()
            result = RangeStretchForm.show_dialog(self)
            if result is None:
                return
            p1, p2, q3, q4 = result
            self.image.stretch_range(p1, p2, q3, q4)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def posterize(self):
        from forms.posterize_form import PosterizeForm

        try:
            self.check_gray()
            result = PosterizeForm.show_dialog(self)
            if result is None:
                return
            lvls = result
            self.image.posterize(lvls)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def blur(self):
        from forms.blur_form import BlurForm

        try:
            result = BlurForm.show_dialog(self)
            if result is None:
                return
            size = result
            self.image.blur(size)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def gblur(self):
        from forms.gblur_form import GBlurForm

        try:
            result = GBlurForm.show_dialog(self)
            if result is None:
                return
            kernel_size, sigma_x, sigma_y, padding = result
            self.image.gaussian_blur(kernel_size, sigma_x, sigma_y, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def sobel(self):
        from forms.sobel_form import SobelForm

        try:
            self.check_gray()
            result = SobelForm.show_dialog(self)
            if result is None:
                return
            kernel_size, ddepth, padding = result
            self.image.sobel(kernel_size, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def prewitt(self):
        from forms.prewitt_form import PrewittForm

        try:
            self.check_gray()
            result = PrewittForm.show_dialog(self)
            if result is None:
                return
            kernel, ddepth, padding = result
            self.image.convolve(kernel, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def laplacian(self):
        from forms.laplacian_form import LaplacianForm

        try:
            self.check_gray()
            result = LaplacianForm.show_dialog(self)
            if result is None:
                return
            kernel_size, ddepth, padding = result
            self.image.laplacian(kernel_size, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def canny(self):
        from forms.canny_form import CannyForm

        try:
            self.check_gray()
            result = CannyForm.show_dialog(self)
            if result is None:
                return
            th1, th2 = result
            self.image.canny(th1, th2)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def laplasharpen(self):
        from forms.laplasharpen_form import LaplaSharpenForm

        try:
            self.check_gray()
            result = LaplaSharpenForm.show_dialog(self)
            if result is None:
                return
            kernel, ddepth, padding = result
            self.image.convolve(kernel, ddepth, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def convolve(self):
        from forms.convolve_form import ConvolveForm

        try:
            self.check_gray()
            result = ConvolveForm.show_dialog(self)
            if result is None:
                return
            kernel, ddepth, padding, should_normalize = result
            self.image.convolve(kernel, ddepth, padding, should_normalize)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def two_stage_filter(self):
        from forms.two_stage_filter_form import TwoStageFilterForm

        try:
            self.check_gray()
            result = TwoStageFilterForm.show_dialog(self)
            if result is None:
                return
            kernel, ddepth, padding, should_normalize = result
            self.image.convolve(kernel, ddepth, padding, should_normalize)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def median(self):
        from forms.median_form import MedianForm

        try:
            result = MedianForm.show_dialog(self)
            if result is None: return
            size, padding = result
            self.image.median(size, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def add_image(self):
        from image_arithmetic import add_image
        try:
            add_image(self)
        except Exception as error:
            ErrorBox(error)

    def subtract_image(self):
        from image_arithmetic import subtract_image

        try:
            subtract_image(self)
        except Exception as error:
            ErrorBox(error)

    def bitwise_and_image(self):
        from image_arithmetic import bitwise_and_image

        try:
            bitwise_and_image(self)
        except Exception as error:
            ErrorBox(error)

    def bitwise_or_image(self):
        from image_arithmetic import bitwise_or_image

        try:
            bitwise_or_image(self)
        except Exception as error:
            ErrorBox(error)

    def bitwise_xor_image(self):
        from image_arithmetic import bitwise_xor_image

        try:
            bitwise_xor_image(self)
        except Exception as error:
            ErrorBox(error)

    def bitwise_not_image(self):
        from image_arithmetic import bitwise_not_image

        try:
            bitwise_not_image(self)
        except Exception as error:
            ErrorBox(error)

    def blend_image(self):
        from image_arithmetic import blend_image

        try:
            blend_image(self)
        except Exception as error:
            ErrorBox(error)

    def erode(self):
        from forms.morphology_form import MorphologyForm

        try:
            self.check_binary()
            result = MorphologyForm.show_dialog("Erosion", self)
            if result is None: return
            shape, size, padding = result
            kernel = structuring_element(shape, size)
            self.image.erode(kernel, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def dilate(self):
        from forms.morphology_form import MorphologyForm

        try:
            self.check_binary()
            result = MorphologyForm.show_dialog("Dilation", self)
            if result is None: return
            shape, size, padding = result
            kernel = structuring_element(shape, size)
            self.image.dilate(kernel, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def morph_open(self):
        from forms.morphology_form import MorphologyForm

        try:
            self.check_binary()
            result = MorphologyForm.show_dialog("Opening", self)
            if result is None: return
            shape, size, padding = result
            kernel = structuring_element(shape, size)
            self.image.morph_open(kernel, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def morph_close(self):
        from forms.morphology_form import MorphologyForm

        try:
            self.check_binary()
            result = MorphologyForm.show_dialog("Closing", self)
            if result is None: return
            shape, size, padding = result
            kernel = structuring_element(shape, size)
            self.image.morph_close(kernel, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def skeletonize(self):
        from forms.morphology_form import MorphologyForm

        try:
            self.check_binary()
            result = MorphologyForm.show_dialog("Skeletonization", self)
            if result is None: return
            shape, size, padding = result
            kernel = structuring_element(shape, size)
            self.image.skeletonize(kernel, padding)
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def hough(self):
        from forms.hough_form import HoughForm

        try:
            self.check_gray()
            result = HoughForm.show_dialog(self)
            if result is None: return
            rho, theta, threshold = result
            theta = theta * np.pi / 180
            new_image = self.image.hough(rho, theta, threshold)
            new_window = ImageWindow(new_image)
            new_window.show()
        except Exception as error:
            ErrorBox(error)

    def profile_line(self):
        from forms.profile_line_form import ProfileLineForm
        from profile_line_window import ProfileLineWindow

        try:
            self.check_gray()
            result = ProfileLineForm.show_dialog(self.image, self)
            if result is None: return
            x1, y1, x2, y2 = result
            line = bresenham(x1, y1, x2, y2)
            profile_window = ProfileLineWindow(self.image, line, self)
            profile_window.show()
        except Exception as error:
            ErrorBox(error)

    def pyramid(self):
        from forms.pyramid_form import PyramidForm

        try:
            result = PyramidForm.show_dialog(self)
            if result is None: return
            do_quarter, do_half, do_double, do_quadruple = result
            skip_quarter, skip_half, skip_double, skip_quadruple = (
                not do_quarter, not do_half, not do_double, not do_quadruple)
            pyramid = self.image.pyramid(skip_quarter, skip_half, skip_double, skip_quadruple)
            for image in pyramid:
                new_window = ImageWindow(image)
                new_window.show()

        except Exception as error:
            ErrorBox(error)

    def thresholding(self):
        from forms.thresholding_form import ThresholdingForm

        try:
            self.check_gray()
            result = ThresholdingForm.show_dialog(self)
            if result is None: return
            th, inv = result
            self.image.thresholding(th, inv)
            self.refresh_image()

        except Exception as error:
            ErrorBox(error)

    def adaptive_thresholding(self):
        from forms.adaptive_thresholding_form import AdaptiveThresholdingForm

        try:
            self.check_gray()
            result = AdaptiveThresholdingForm.show_dialog(self)
            if result is None: return
            block_size, gaussian_mode, c, inv = result
            self.image.adaptive_thresholding(block_size, c, gaussian_mode, inv)
            self.refresh_image()

        except Exception as error:
            ErrorBox(error)

    def otsu_thresholding(self):
        from forms.otsu_form import OtsuForm

        try:
            self.check_gray()
            result = OtsuForm.show_dialog(self)
            if result is None: return
            inv = result
            self.image.otsu_thresholding(inv)
            self.refresh_image()

        except Exception as error:
            ErrorBox(error)

    def grabcut_rect(self):
        from forms.grabcut_rect_form import GrabCutRectForm

        try:
            result = GrabCutRectForm.show_dialog(self)
            if result is None: return
            x, y, w, h, iter_count = result
            new_image = self.image.grabcut_rect((x, y, w, h), iter_count)
            new_window = ImageWindow(new_image)
            new_window.show()

        except Exception as error:
            ErrorBox(error)

    def grabcut_mask(self):
        from forms.grabcut_mask_form import GrabCutMaskForm

        try:
            result = GrabCutMaskForm.show_dialog(self)
            if result is None: return
            mask, iter_count = result
            new_image = self.image.grabcut_mask(mask, iter_count)
            new_window = ImageWindow(new_image)
            new_window.show()

        except Exception as error:
            ErrorBox(error)

    def watershed(self):
        from forms.watershed_form import WatershedForm

        try:
            result = WatershedForm.show_dialog(self)
            if result is None: return
            do_boundaries, do_colors, do_bin, inv = result
            boundaries, colors, binary, found = self.image.watershed(inv)
            if do_boundaries:
                new_window = ImageWindow(boundaries)
                new_window.show()
            if do_colors:
                new_window = ImageWindow(colors)
                new_window.show()
            if do_bin:
                new_window = ImageWindow(binary)
                new_window.show()

            InfoBox("Watershed", f"{found} objects have been found.")

        except Exception as error:
            ErrorBox(error)

    def inpaint(self):
        from forms.inpainting_form import InpaintingForm

        try:
            result = InpaintingForm.show_dialog(self)
            if result is None: return
            mask, iter_count, mode = result
            inpainted = None
            match mode:
                case "TELEA":
                    inpainted = self.image.inpaint_telea(mask, iter_count)
                case "NS":
                    inpainted = self.image.inpaint_ns(mask, iter_count)
                case _:
                    raise ValueError("Something went wrong establishing the mode!")
            new_window = ImageWindow(inpainted)
            new_window.show()

        except Exception as error:
            ErrorBox(error)

    def colorful_contours(self):
        from forms.contour_extraction_form import ContourExtractionForm

        try:
            self.check_binary()
            result = ContourExtractionForm.show_dialog(self)
            if result is None: return
            mode, approximation = result
            contours = self.image.get_contours(mode, approximation)

            contours_count = len(contours)
            InfoBox("Results", f"{contours_count} contours have been found!")

            new_image = self.image.colorful_contours(contours, False, None)
            new_window = ImageWindow(new_image)
            new_window.show()

        except Exception as error:
            ErrorBox(error)

    def object_traits(self):
        from forms.contour_extraction_form import ContourExtractionForm

        try:
            self.check_binary()
            result = ContourExtractionForm.show_dialog(self, "Object Traits")
            if result is None: return
            mode, approximation = result
            contours = self.image.get_contours(mode, approximation)
            if len(contours) == 0:
                raise ValueError("No contours have been found.")
            traits_window = ObjectTraitsWindow(contours, self)
            traits_window.show()

        except Exception as error:
            ErrorBox(error)

    def _save_file_dialog(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setFileMode(QFileDialog.AnyFile)

        filters = [
            "BMP Files (*.bmp)",
            "JPG Files (*.jpg)",
            "PNG Files (*.png)",
            "All Files (*.*)",
        ]
        dlg.setNameFilters(filters)

        file_name, ext = os.path.splitext(self.image.name)
        idx_list = [i for i, filt in enumerate(filters) if ext.lower() in filt]
        idx = idx_list[0] if len(idx_list) > 0 else -1

        dlg.selectNameFilter(filters[idx])
        dlg.selectFile(file_name)
        dlg.setDefaultSuffix(ext)

        dlg.exec()

        result = dlg.selectedFiles()
        if len(result) > 0 and dlg.result() == QFileDialog.Accepted:
            result = result[0]
            return result
        else:
            return None

    def save(self):
        try:
            path = self._save_file_dialog()
            if path is not None:
                self.image.save_to_file(path)
                InfoBox("Success!", "File saved successfully!")
        except Exception as e:
            ErrorBox("Something went wrong!")

    def save_rle(self):
        from rle_window import RLEWindow
        try:
            self.check_gray()
            rle_window = RLEWindow(self.image, self)
            rle_window.show()

        except Exception as e:
            ErrorBox(e)



