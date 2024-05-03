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
YELLOW = (255, 220, 0)


class ContourExtractionForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None, title: str = "Contour Extraction"):
        super().__init__()

        self.mode_options = ["LIST", "EXTERNAL"]
        self.mode = self.mode_options[0]
        self.approximation_options = ["SIMPLE", "TC89_L1", "TC89_KCOS", "NONE"]
        self.approximation = self.approximation_options[0]

        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | {title}"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.mode_combo_box = QComboBox()
        self.mode_combo_box.addItems(self.mode_options)
        self.mode_combo_box.currentIndexChanged.connect(self.mode_idx_changed)
        self.mode_combo_box.setCurrentIndex(0)
        form_layout.addRow("Mode", self.mode_combo_box)

        self.appr_combo_box = QComboBox()
        self.appr_combo_box.addItems(self.approximation_options)
        self.appr_combo_box.currentIndexChanged.connect(self.appr_idx_changed)
        self.appr_combo_box.setCurrentIndex(0)
        form_layout.addRow("Approximation", self.appr_combo_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        # self.setFixedSize(super().size().width() // 2 - 20, super().size().height() + 25)

    @property
    def is_data_valid(self):
        c1 = self.approximation in self.approximation_options
        c2 = self.mode in self.mode_options
        return c1 and c2

    def mode_idx_changed(self, idx):
        self.mode = self.mode_options[idx]

    def appr_idx_changed(self, idx):
        self.approximation = self.approximation_options[idx]

    def accept(self):
        if self.is_data_valid:
            super().accept()
        else:
            ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None, title: str = "Contour Extraction") -> tuple[str, str] | None:
        cef = ContourExtractionForm(parent)
        cef.setModal(True)
        result = cef.exec()
        return (cef.mode, cef.approximation) \
            if result == QDialog.Accepted else None
