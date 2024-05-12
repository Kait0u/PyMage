import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QDialog, QDialogButtonBox, QComboBox)

from error_box import ErrorBox
from forms.form_widgets.np_tablewidget import NpTableWidget
from image import DesiredDepth, Padding
from masks.laplace_masks import LaplaSharpen


class LaplaSharpenForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.filter_options = [LaplaSharpen.CROSS_5, LaplaSharpen.SQUARE_5, LaplaSharpen.SQUARE_9]
        self.filter = self.filter_options[0]
        self.filter_np = self.filter.value
        self.ddepth_options = [DesiredDepth.U8, DesiredDepth.F64]
        self.ddepth = self.ddepth_options[0]
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]
        self.padding = self.padding_options[0]

        title = "LaplaSharpen"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | LaplaSharpen"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget1 = QWidget()
        form_layout1 = QFormLayout()
        form_widget1.setLayout(form_layout1)
        main_layout.addWidget(form_widget1)

        self.filter_combo_box = QComboBox()
        self.filter_combo_box.addItems(list(map(
            lambda item: item.name,
            self.filter_options
        )))
        self.filter_combo_box.currentIndexChanged.connect(self.filter_idx_changed)
        form_layout1.addRow("Filter", self.filter_combo_box)

        self.filter_table = NpTableWidget(self.filter_np)
        main_layout.addWidget(self.filter_table)

        form_widget2 = QWidget()
        form_layout2 = QFormLayout()
        form_widget2.setLayout(form_layout2)
        main_layout.addWidget(form_widget2)

        self.ddepth_combo_box = QComboBox()
        self.ddepth_combo_box.addItems(list(map(
            lambda item: item.name,
            self.ddepth_options
        )))
        self.ddepth_combo_box.currentIndexChanged.connect(self.ddepth_idx_changed)
        form_layout2.addRow("Desired Depth", self.ddepth_combo_box)

        self.padding_combo_box = QComboBox()
        self.padding_combo_box.addItems(list(map(
            lambda item: item.name,
            self.padding_options
        )))
        self.padding_combo_box.currentIndexChanged.connect(self.padding_idx_changed)
        form_layout2.addRow("Padding", self.padding_combo_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setFixedSize(super().size().height() // 2 + 80, super().size().height() - 20)

    @property
    def is_data_valid(self):
        c1 = self.filter in self.filter_options
        c2 = self.ddepth in self.ddepth_options
        c3 = self.padding in self.padding_options
        return c1 and c2 and c3

    def filter_idx_changed(self, idx):
        self.filter = self.filter_options[idx]
        self.filter_np = self.filter.value
        self.filter_table.data = self.filter_np

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def ddepth_idx_changed(self, idx):
        self.ddepth = self.ddepth_options[idx]

    def accept(self):
        if self.is_data_valid:
            self.filter = self.filter.value
            super().accept()
        else:
            ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[np.ndarray, DesiredDepth, Padding] | None:
        lsf = LaplaSharpenForm(parent)
        lsf.setModal(True)
        result = lsf.exec()
        return (lsf.filter_np, lsf.ddepth, lsf.padding) \
            if result == QDialog.Accepted else None


