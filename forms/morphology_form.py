from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QComboBox)

from error_box import ErrorBox
from image import Padding, StructuringElementShape


class MorphologyForm(QDialog):
    def __init__(self, op_name: str, parent: QMainWindow | None = None):
        super().__init__()
        self.kernel_shape = StructuringElementShape.RECTANGLE
        self.kernel_shape_options = [StructuringElementShape.RECTANGLE,
                                     StructuringElementShape.RHOMBUS,
                                     StructuringElementShape.ELLIPSE,
                                     StructuringElementShape.CROSS]
        self.size = 3
        self.padding = Padding.REPLICATE
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]

        title = op_name
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | {op_name}"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.kernel_shape_combo_box = QComboBox()
        self.kernel_shape_combo_box.addItems(list(map(
            lambda item: item.name,
            self.kernel_shape_options
        )))
        self.kernel_shape_combo_box.currentIndexChanged.connect(self.kernel_shape_idx_changed)
        form_layout.addRow("Structuring Element: ", self.kernel_shape_combo_box)

        self.size_spin_box = QSpinBox()
        self.size_spin_box.setMinimum(3)
        self.size_spin_box.setValue(self.size)
        self.size_spin_box.setSingleStep(2)
        self.size_spin_box.valueChanged.connect(self.size_value_changed)

        form_layout.addRow("Size", self.size_spin_box)

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
        return self.size % 2 == 1 and self.size > 2

    def size_value_changed(self, val):
        self.size = val

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def kernel_shape_idx_changed(self, idx):
        self.kernel_shape = self.kernel_shape_options[idx]

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(op_name: str, parent=None) -> int | None:
        mf = MorphologyForm(op_name, parent)
        mf.setModal(True)
        result = mf.exec()
        return (mf.kernel_shape, mf.size, mf.padding) if result == QDialog.Accepted else None


