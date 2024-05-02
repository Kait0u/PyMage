from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox, QLabel)

from image import ColorModes, Image

MAX_SIZE = 256


class ThresholdingForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()

        self.orig_image: Image = parent.image
        self.image: Image = self.orig_image.copy()

        self.threshold = 255 // 2
        self.inv = False

        title = "Thresholding"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Thresholding"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.th_spin_box = QSpinBox()
        self.th_spin_box.setMinimum(0)
        self.th_spin_box.setMaximum(255)
        self.th_spin_box.setValue(self.threshold)
        self.th_spin_box.valueChanged.connect(self.th_value_changed)
        form_layout.addRow("Threshold", self.th_spin_box)

        self.inv_checkbox = QCheckBox()
        self.inv_checkbox.setTristate(False)
        self.inv_checkbox.setChecked(self.inv)
        self.inv_checkbox.stateChanged.connect(self.inv_toggled)
        form_layout.addRow("Inverted", self.inv_checkbox)

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
        c1 = 0 <= self.threshold <= 255
        return c1

    def th_value_changed(self, val):
        self.threshold = val
        self.update_preview()

    def inv_toggled(self, val):
        self.inv = self.inv_checkbox.isChecked()
        self.update_preview()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    def refresh_image(self):
        color_format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

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
        self.image.thresholding(self.threshold, self.inv)
        self.refresh_image()


    @staticmethod
    def show_dialog(parent=None) -> tuple[int, bool] | None:
        tf = ThresholdingForm(parent)
        tf.setModal(True)
        result = tf.exec()
        return (tf.threshold, tf.inv) \
            if result == QDialog.Accepted else None


