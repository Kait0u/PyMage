import cv2 as cv
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox, QLabel,
                             QHBoxLayout)

from error_box import ErrorBox
from image import ColorModes, Image

LMIN = 0
LMAX = 255
MAX_SIZE = 256
PREVIEW_BRIGHTNESS = 30


class GrabCutRectForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()

        self.orig_image: Image = parent.image
        self.image: Image = self.orig_image.copy()
        self.img_w = self.image.width
        self.img_h = self.image.height

        self.x = 50
        self.y = 50
        self.width = 100
        self.height = 100
        self.iter_count = 3

        title = "GrabCut"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | GrabCut"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        coords_widget = QWidget()
        coords_layout = QHBoxLayout()
        coords_widget.setLayout(coords_layout)
        main_layout.addWidget(coords_widget)

        left_coords_widget = QWidget()
        left_coords_layout = QFormLayout()
        left_coords_widget.setLayout(left_coords_layout)
        coords_layout.addWidget(left_coords_widget)

        right_coords_widget = QWidget()
        right_coords_layout = QFormLayout()
        right_coords_widget.setLayout(right_coords_layout)
        coords_layout.addWidget(right_coords_widget)

        self.x_spin_box = QSpinBox()
        self.x_spin_box.setMinimum(0)
        self.x_spin_box.setMaximum(self.img_w - 1)
        self.x_spin_box.setValue(self.x)
        self.x_spin_box.valueChanged.connect(self.x_value_changed)
        left_coords_layout.addRow("X", self.x_spin_box)

        self.y_spin_boy = QSpinBox()
        self.y_spin_boy.setMinimum(0)
        self.y_spin_boy.setMaximum(self.img_h - 1)
        self.y_spin_boy.setValue(self.y)
        self.y_spin_boy.valueChanged.connect(self.y_value_changed)
        left_coords_layout.addRow("Y", self.y_spin_boy)

        self.w_spin_box = QSpinBox()
        self.w_spin_box.setMinimum(0)
        self.w_spin_box.setMaximum(self.img_w - 1 - self.x)
        self.w_spin_box.setValue(self.width)
        self.w_spin_box.valueChanged.connect(self.w_value_changed)
        right_coords_layout.addRow("Width", self.w_spin_box)

        self.h_spin_box = QSpinBox()
        self.h_spin_box.setMinimum(0)
        self.h_spin_box.setMaximum(self.img_h - 1 - self.y)
        self.h_spin_box.setValue(self.height)
        self.h_spin_box.valueChanged.connect(self.h_value_changed)
        right_coords_layout.addRow("Height", self.h_spin_box)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.iter_spin_box = QSpinBox()
        self.iter_spin_box.setMinimum(1)
        self.iter_spin_box.setMaximum(32)
        self.iter_spin_box.setValue(self.iter_count)
        self.iter_spin_box.valueChanged.connect(self.iter_count_value_changed)
        form_layout.addRow("Iterations", self.iter_spin_box)

        # Preview

        preview_widget = QGroupBox()
        preview_widget.setTitle("Preview")
        preview_layout = QVBoxLayout()
        preview_widget.setLayout(preview_layout)
        main_layout.addWidget(preview_widget)

        self.image_frame = QLabel()
        self.image_frame.setMinimumSize(MAX_SIZE, MAX_SIZE)
        self.image_frame.setMaximumSize(MAX_SIZE, MAX_SIZE)
        preview_layout.addWidget(self.image_frame)

        self.update_preview()

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setFixedSize(super().size().width() // 2 - 20, super().size().height() + 25)

    @property
    def is_data_valid(self):
        c1 = 0 <= self.x < self.img_w
        c2 = 0 <= self.y < self.img_h
        c3 = 0 < self.width <= self.img_w - 1 - self.x
        c4 = 0 < self.height <= self.img_h - 1 - self.y
        return c1 and c2 and c3 and c4

    def x_value_changed(self, val):
        self.x = val
        self.w_spin_box.setMaximum(self.img_w - 1 - self.x)
        self.update_preview()

    def y_value_changed(self, val):
        self.y = val
        self.h_spin_box.setMaximum(self.img_h - 1 - self.y)
        self.update_preview()

    def w_value_changed(self, val):
        self.width = val
        self.update_preview()

    def h_value_changed(self, val):
        self.height = val
        self.update_preview()

    def iter_count_value_changed(self, val):
        self.iter_count = val

    def accept(self):
        if self.is_data_valid:
            super().accept()
        else:
            ErrorBox("Invalid data")

    def draw_rectangle(self):
        if self.is_data_valid:
            x1 = self.x
            x2 = self.x + self.width
            y1 = self.y
            y2 = self.y + self.height

            mask = np.zeros_like(self.image.img)
            mask[y1: y2 + 1, x1: x2 + 1] = 1

            self.image.img = (1 - mask) * self.image.img + mask * self.orig_image.img

    def refresh_image(self):
        color_format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

        brightness_factor = PREVIEW_BRIGHTNESS / 100
        self.image.img = np.uint8(np.clip(self.image.img * brightness_factor, LMIN, LMAX))
        self.draw_rectangle()

        qt_image = QImage(self.image.img, self.image.width,
                          self.image.height, self.image.img.strides[0], color_format)

        w = self.image.width
        h = self.image.height

        if w > h:
            ratio = h / w
            w = MAX_SIZE
            h = int(MAX_SIZE * ratio)
        else:
            ratio = w / h
            h = MAX_SIZE
            w = int(MAX_SIZE * ratio)

        qt_image = QPixmap.fromImage(qt_image).scaled(w, h)
        self.image_frame.setPixmap(qt_image)
        self.image_frame.setAlignment(Qt.AlignCenter)

    def update_preview(self):
        self.image = self.orig_image.copy()
        self.refresh_image()

    @staticmethod
    def show_dialog(parent=None) -> tuple[int, int, int, int, int] | None:
        gcrf = GrabCutRectForm(parent)
        gcrf.setModal(True)
        result = gcrf.exec()
        return (gcrf.x, gcrf.y, gcrf.width, gcrf.height, gcrf.iter_count) \
            if result == QDialog.Accepted else None
