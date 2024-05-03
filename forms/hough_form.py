from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox)

from error_box import ErrorBox


class HoughForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.rho = 1.0
        self.theta = 1.0
        self.threshold = 200

        title = "Hough"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Hough"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.rho_spin_box = QDoubleSpinBox()
        self.rho_spin_box.setMinimum(0)
        self.rho_spin_box.setValue(self.rho)
        self.rho_spin_box.setSingleStep(0.1)
        self.rho_spin_box.valueChanged.connect(self.rho_value_changed)
        form_layout.addRow("ρ", self.rho_spin_box)

        self.theta_spin_box = QDoubleSpinBox()
        self.theta_spin_box.setMinimum(0)
        self.theta_spin_box.setValue(self.theta)
        self.theta_spin_box.setSingleStep(0.1)
        self.theta_spin_box.valueChanged.connect(self.theta_value_changed)
        form_layout.addRow("θ (°)", self.theta_spin_box)

        self.th_spin_box = QSpinBox()
        self.th_spin_box.setRange(0, 2000)
        self.th_spin_box.setValue(self.threshold)
        self.th_spin_box.valueChanged.connect(self.th_value_changed)
        form_layout.addRow("Threshold", self.th_spin_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setFixedSize(super().size().width() // 3, super().size().height() // 3 - 15)

    @property
    def is_data_valid(self):
        c1 = 0 < self.rho
        c2 = 0 < self.theta < 180
        c3 = 0 <= self.threshold

        return c1 and c2 and c3

    def th_value_changed(self, val):
        self.threshold = val

    def rho_value_changed(self, val):
        self.rho = val

    def theta_value_changed(self, val):
        self.theta = val

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[float, float, int] | None:
        hf = HoughForm(parent)
        hf.setModal(True)
        result = hf.exec()
        return (hf.rho, hf.theta, hf.threshold) \
            if result == QDialog.Accepted else None

