from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)


class AdaptiveThresholdingForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.block_size = 3
        self.gaussian_mode = False
        self.c = 2.0
        self.inv = False


        title = "Adaptive Thresholding"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Adaptive Thresholding"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.block_size_spin_box = QSpinBox()
        self.block_size_spin_box.setMinimum(3)
        self.block_size_spin_box.setValue(self.block_size)
        self.block_size_spin_box.setSingleStep(2)
        self.block_size_spin_box.valueChanged.connect(self.block_size_value_changed)
        form_layout.addRow("Block Size", self.block_size_spin_box)

        self.gau_checkbox = QCheckBox()
        self.gau_checkbox.setTristate(False)
        self.gau_checkbox.setChecked(self.gaussian_mode)
        self.gau_checkbox.stateChanged.connect(self.gau_toggled)
        form_layout.addRow("Gaussian Mode", self.gau_checkbox)

        self.c_spin = QDoubleSpinBox()
        self.c_spin.setValue(self.c)
        self.c_spin.setSingleStep(0.1)
        self.c_spin.valueChanged.connect(self.c_value_changed)
        form_layout.addRow("C", self.c_spin)


        self.inv_checkbox = QCheckBox()
        self.inv_checkbox.setTristate(False)
        self.inv_checkbox.setChecked(self.inv)
        self.inv_checkbox.stateChanged.connect(self.inv_toggled)
        form_layout.addRow("Inverted", self.inv_checkbox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    @property
    def is_data_valid(self):
        c1 = 3 <= self.block_size and self.block_size % 2 == 1
        return c1

    def block_size_value_changed(self, val):
        self.block_size = val

    def gau_toggled(self, val):
        self.gaussian_mode = self.gau_checkbox.isChecked()

    def c_value_changed(self, val):
        self.c = val

    def inv_toggled(self, val):
        self.inv = self.inv_checkbox.isChecked()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[int, bool, float, bool] | None:
        atf = AdaptiveThresholdingForm(parent)
        atf.setModal(True)
        result = atf.exec()
        return (atf.block_size, atf.gaussian_mode, atf.c, atf.inv) \
            if result == QDialog.Accepted else None


