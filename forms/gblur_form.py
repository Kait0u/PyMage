from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)

from image import Padding


class GBlurForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.size = 3
        self.sigma_x = 1
        self.sigma_y = 1
        self.sigma_y_mimics_x = True
        self.padding = Padding.REPLICATE
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]

        title = "Gaussian Blur"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Gaussian Blur"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.size_spin_box = QSpinBox()
        self.size_spin_box.setMinimum(3)
        self.size_spin_box.setValue(self.size)
        self.size_spin_box.setSingleStep(2)
        self.size_spin_box.valueChanged.connect(self.size_value_changed)
        form_layout.addRow("Size", self.size_spin_box)

        self.sigma_x_spin_box = QDoubleSpinBox()
        self.sigma_x_spin_box.setMinimum(0.0)
        self.sigma_x_spin_box.setSingleStep(0.1)
        self.sigma_x_spin_box.valueChanged.connect(self.sigma_x_value_changed)
        form_layout.addRow("σx", self.sigma_x_spin_box)

        self.sigma_y_copy_checkbox = QCheckBox()
        self.sigma_y_copy_checkbox.setCheckState(self.sigma_y_mimics_x)
        self.sigma_y_copy_checkbox.setTristate(False)
        self.sigma_y_copy_checkbox.stateChanged.connect(self.sigma_y_copy_checkbox_toggled)
        form_layout.addRow("σy mimics σx", self.sigma_y_copy_checkbox)

        self.sigma_y_spin_box = QDoubleSpinBox()
        self.sigma_y_spin_box.setMinimum(0.0)
        self.sigma_y_spin_box.setSingleStep(0.1)
        self.sigma_y_spin_box.valueChanged.connect(self.sigma_y_value_changed)
        form_layout.addRow("σy", self.sigma_y_spin_box)


        self.padding_combo_box = QComboBox()
        self.padding_combo_box.addItems(list(map(
            lambda item: item.name,
            self.padding_options
        )))
        self.padding_combo_box.currentIndexChanged.connect(self.padding_idx_changed)
        form_layout.addRow("Padding", self.padding_combo_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    @property
    def is_data_valid(self):
        c1 = self.size % 2 == 1 and self.size > 2
        c2 = 0 <= self.sigma_x
        c3 = 0 <= self.sigma_y
        c4 = self.padding in self.padding_options
        return c1 and c2 and c3 and c4

    def size_value_changed(self, val):
        self.size = val

    def sigma_x_value_changed(self, val):
        self.sigma_x = val
        if self.sigma_y_mimics_x:
            self.sigma_y = self.sigma_x
            self.sigma_y_spin_box.setValue(self.sigma_x)

    def sigma_y_value_changed(self, val):
        self.sigma_y = val

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def sigma_y_copy_checkbox_toggled(self, val):
        self.sigma_y_mimics_x = val
        self.sigma_y_spin_box.setEnabled(not val)

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> int | None:
        gbf = GBlurForm(parent)
        gbf.setModal(True)
        result = gbf.exec()
        return (gbf.size, gbf.sigma_x, gbf.sigma_y, gbf.padding) \
            if result == QDialog.Accepted else None


