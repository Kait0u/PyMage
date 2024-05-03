from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QLabel)

from error_box import ErrorBox
from image import Image


class ProfileLineForm(QDialog):
    def __init__(self, image: Image,  parent: QMainWindow | None = None):
        super().__init__()
        self.xmax, self.ymax = image.img.shape

        self.x1 = 0
        self.y1 = 0
        self.x2 = self.xmax - 1
        self.y2 = self.ymax - 1

        title = "Profile Line"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Profile Line"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.x1_spin_box = QSpinBox()
        self.x1_spin_box.setMinimum(0)
        self.x1_spin_box.setMaximum(self.xmax - 1)
        self.x1_spin_box.setValue(self.x1)
        self.x1_spin_box.valueChanged.connect(self.x1_value_changed)
        form_layout.addRow("X1", self.x1_spin_box)

        self.y1_spin_box = QSpinBox()
        self.y1_spin_box.setMinimum(0)
        self.y1_spin_box.setMaximum(self.ymax - 1)
        self.y1_spin_box.setValue(self.y1)
        self.y1_spin_box.valueChanged.connect(self.y1_value_changed)
        form_layout.addRow("Y1", self.y1_spin_box)

        form_layout.addWidget(QLabel())

        self.x2_spin_box = QSpinBox()
        self.x2_spin_box.setMinimum(0)
        self.x2_spin_box.setMaximum(self.xmax - 1)
        self.x2_spin_box.setValue(self.x2)
        self.x2_spin_box.valueChanged.connect(self.x2_value_changed)
        form_layout.addRow("X2", self.x2_spin_box)

        self.y2_spin_box = QSpinBox()
        self.y2_spin_box.setMinimum(0)
        self.y2_spin_box.setMaximum(self.ymax - 1)
        self.y2_spin_box.setValue(self.y2)
        self.y2_spin_box.valueChanged.connect(self.y2_value_changed)
        form_layout.addRow("Y2", self.y2_spin_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setFixedSize(super().size().width() // 3, super().size().height() // 2 - 60)

    @property
    def is_data_valid(self):
        c1 = 0 <= self.x1 < self.xmax
        c2 = 0 <= self.x2 < self.xmax
        c3 = 0 <= self.y1 < self.ymax
        c4 = 0 <= self.y2 < self.ymax

        return c1 and c2 and c3 and c4

    def x1_value_changed(self, val):
        self.x1 = val

    def y1_value_changed(self, val):
        self.y1 = val

    def x2_value_changed(self, val):
        self.x2 = val

    def y2_value_changed(self, val):
        self.y2 = val

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(image: Image, parent=None) -> tuple[int, int, int, int] | None:
        plf = ProfileLineForm(image, parent)
        plf.setModal(True)
        result = plf.exec()
        return (plf.x1, plf.y1, plf.x2, plf.y2) \
            if result == QDialog.Accepted else None


