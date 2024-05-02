import cv2 as cv
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox, QLabel,
                             QHBoxLayout)

from error_box import ErrorBox
from forms.form_widgets.open_file_widget import OpenFileWidget
from image import ColorModes, Image

LMIN = 0
LMAX = 255
MAX_SIZE = 256
PREVIEW_BRIGHTNESS = 30


class GrabCutMaskForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()

        self.orig_image: Image = parent.image
        self.image: Image = self.orig_image.copy()

        self.mask = np.zeros_like(self.image.img)
        self.iter_count = 3

        title = "GrabCut"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | GrabCut"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        path_group_widget = QGroupBox()
        path_group_widget.setTitle("Mask Path")
        path_layout = QVBoxLayout()
        path_group_widget.setLayout(path_layout)
        main_layout.addWidget(path_group_widget)

        self.path_widget = OpenFileWidget()
        self.path_widget.valueChanged.connect(self.path_value_changed)
        path_layout.addWidget(self.path_widget)

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

    @property
    def is_data_valid(self):
        c1 = self.mask.shape[:2] == self.image.img.shape[:2]
        return c1

    def path_value_changed(self, val):
        path = val

        try:
            img = Image.from_file(path, True)
        except Exception as e:
            ErrorBox("Something went wrong!")
            return

        if (self.image.width, self.image.height) != (img.width, img.height):
            ErrorBox("Incompatible mask size!")
        elif not img.is_binary:
            ErrorBox("This is not a binary mask!")
        else:
            try:
                self.mask = img.img
                self.mask[self.mask == LMIN] = 0
                self.mask[self.mask == LMAX] = 1
                self.update_preview()
            except Exception as e:
                ErrorBox(e)

    def iter_count_value_changed(self, val):
        self.iter_count = val

    def accept(self):
        if self.is_data_valid:
            super().accept()
        else:
            ErrorBox("Invalid data")

    def draw_mask(self):
        if self.is_data_valid:
            mask = self.mask if len(self.mask.shape) > 2 else cv.merge((self.mask, self.mask, self.mask))
            self.image.img = (1 - mask) * self.image.img + mask * self.orig_image.img

    def refresh_image(self):
        color_format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

        brightness_factor = PREVIEW_BRIGHTNESS / 100
        self.image.img = np.uint8(np.clip(self.image.img * brightness_factor, LMIN, LMAX))
        self.draw_mask()

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
    def show_dialog(parent=None) -> tuple[np.ndarray, int] | None:
        gcmf = GrabCutMaskForm(parent)
        gcmf.setModal(True)
        result = gcmf.exec()
        return (gcmf.mask, gcmf.iter_count) \
            if result == QDialog.Accepted else None
