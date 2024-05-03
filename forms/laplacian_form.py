from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)

from error_box import ErrorBox
from image import DesiredDepth, Padding


class LaplacianForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.size = 3
        self.ddepth = DesiredDepth.U8
        self.ddepth_options = [DesiredDepth.U8, DesiredDepth.F64]
        self.padding = Padding.REPLICATE
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]

        title = "Laplacian"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Laplacian"

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

        self.ddepth_combo_box = QComboBox()
        self.ddepth_combo_box.addItems(list(map(
            lambda item: item.name,
            self.ddepth_options
        )))
        self.ddepth_combo_box.currentIndexChanged.connect(self.ddepth_idx_changed)
        form_layout.addRow("Desired Depth", self.ddepth_combo_box)

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

        self.setFixedSize(super().size().width() // 3, super().size().height() // 3 - 15)

    @property
    def is_data_valid(self):
        c1 = self.size % 2 == 1 and self.size > 2
        c2 = self.ddepth in self.ddepth_options
        c3 = self.padding in self.padding_options
        return c1 and c2 and c3

    def size_value_changed(self, val):
        self.size = val

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def ddepth_idx_changed(self, idx):
        self.ddepth = self.ddepth_options[idx]

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[int, DesiredDepth, Padding] | None:
        lf = LaplacianForm(parent)
        lf.setModal(True)
        result = lf.exec()
        return (lf.size, lf.ddepth, lf.padding) \
            if result == QDialog.Accepted else None


