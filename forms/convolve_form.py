import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QTableView,
                             QAbstractItemView, QTableWidget, QHeaderView)

from forms.form_widgets.np_tablewidget import NpTableWidget
from image import DesiredDepth, Padding


class ConvolveForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.filter_size = 3
        self.filter_size_options = [3, 5, 7]
        self.filter = np.zeros((self.filter_size, self.filter_size))
        self.ddepth = DesiredDepth.U8
        self.ddepth_options = [DesiredDepth.U8, DesiredDepth.F64]
        self.padding = Padding.REPLICATE
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]

        title = "Convolve"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Convolve"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget1 = QWidget()
        form_layout1 = QFormLayout()
        form_widget1.setLayout(form_layout1)
        main_layout.addWidget(form_widget1)

        self.filter_combo_box = QComboBox()
        self.filter_combo_box.addItems(list(map(str, self.filter_size_options)))
        self.filter_combo_box.currentIndexChanged.connect(self.filter_size_idx_changed)
        form_layout1.addRow("Filter Size", self.filter_combo_box)

        self.filter_table = NpTableWidget.empty_editable(self.filter_size, self.filter_size)
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
        self.button_box.accepted.connect(self.update_filter)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def filter_size_idx_changed(self, idx):
        self.filter_size = self.filter_size_options[idx]
        layout = self.filter_table.parent().layout()

        new_table = NpTableWidget.empty_editable(self.filter_size, self.filter_size)

        layout.replaceWidget(self.filter_table, new_table)
        self.filter_table = new_table

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def ddepth_idx_changed(self, idx):
        self.ddepth = self.ddepth_options[idx]

    def update_filter(self):
        self.filter = self.filter_table.extract_numpy()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[np.ndarray, DesiredDepth, Padding] | None:
        cf = ConvolveForm(parent)
        cf.setModal(True)
        result = cf.exec()
        return (cf.filter, cf.ddepth, cf.padding) \
            if result == QDialog.Accepted else None