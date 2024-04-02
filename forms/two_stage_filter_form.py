import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QTableView,
                             QAbstractItemView, QTableWidget, QHeaderView, QHBoxLayout, QLabel, QFrame)

from forms.form_widgets.np_tablewidget import NpTableWidget
from image import DesiredDepth, Padding
from utils import convolve_filters


class TwoStageFilterForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.filter_size = 3
        self.filter1 = np.zeros((self.filter_size, self.filter_size))
        self.filter2 = np.zeros((self.filter_size, self.filter_size))
        self.output = np.zeros((self.filter_size * 2 - 1, self.filter_size * 2 - 1))

        self.ddepth = DesiredDepth.U8
        self.ddepth_options = [DesiredDepth.U8, DesiredDepth.F64]
        self.padding = Padding.REPLICATE
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]

        self.should_normalize = True

        title = "Two Stage Filter"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Two Stage Filter"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        filters_widget = QWidget()
        filters_layout = QHBoxLayout()
        filters_widget.setLayout(filters_layout)
        main_layout.addWidget(filters_widget)

        # Filter 1

        filter1_widget = QWidget()
        filter1_layout = QVBoxLayout()
        filter1_widget.setLayout(filter1_layout)
        filters_layout.addWidget(filter1_widget)

        f1_label = QLabel()
        f1_label.setText("F1 (Smoothen)")
        f1_label.setAlignment(Qt.AlignCenter)
        filter1_layout.addWidget(f1_label)

        self.filter1_table = NpTableWidget.empty_editable(self.filter_size, self.filter_size)
        filter1_layout.addWidget(self.filter1_table)

        # Filter 2

        filter2_widget = QWidget()
        filter2_layout = QVBoxLayout()
        filter2_widget.setLayout(filter2_layout)
        filters_layout.addWidget(filter2_widget)

        f2_label = QLabel()
        f2_label.setText("F2 (Sharpen)")
        f2_label.setAlignment(Qt.AlignCenter)
        filter2_layout.addWidget(f2_label)

        self.filter2_table = NpTableWidget.empty_editable(self.filter_size, self.filter_size)
        filter2_layout.addWidget(self.filter2_table)

        # Intersection: convolve button

        convolve_button = QPushButton()
        convolve_button.setText("Convolve (Preview)")
        convolve_button.clicked.connect(self.update_outfilter)
        main_layout.addWidget(convolve_button)

        main_layout.addWidget(horizontal_separator())

        # Filter 3 (Outfilter) --> Result
        outfilter_widget = QWidget()
        outfilter_layout = QVBoxLayout()
        outfilter_widget.setLayout(outfilter_layout)
        main_layout.addWidget(outfilter_widget)

        f3_label = QLabel()
        f3_label.setText("Output Filter")
        f3_label.setAlignment(Qt.AlignCenter)
        outfilter_layout.addWidget(f3_label)

        self.outfilter_table = NpTableWidget(self.output)
        outfilter_layout.addWidget(self.outfilter_table)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.normalize_checkbox = QCheckBox()
        self.normalize_checkbox.setCheckState(self.should_normalize)
        self.normalize_checkbox.setTristate(False)
        self.normalize_checkbox.stateChanged.connect(self.normalize_checkbox_state_changed)
        form_layout.addRow("Normalize", self.normalize_checkbox)

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
        self.button_box.accepted.connect(self.update_filters)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def ddepth_idx_changed(self, idx):
        self.ddepth = self.ddepth_options[idx]

    def update_filters(self):
        self.filter1 = self.filter1_table.extract_numpy()
        self.filter2 = self.filter2_table.extract_numpy()
        self.output = convolve_filters(self.filter1, self.filter2)

    def normalize_checkbox_state_changed(self, value):
        bv = bool(value)
        self.should_normalize = bv

    def update_outfilter(self):
        self.update_filters()
        self.outfilter_table.data = self.output

    @property
    def is_data_valid(self):
        c1 = self.ddepth in self.ddepth_options
        c2 = self.padding in self.padding_options
        return c1 and c2

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[np.ndarray, DesiredDepth, Padding, bool] | None:
        tsff = TwoStageFilterForm(parent)
        tsff.setModal(True)
        result = tsff.exec()
        return (tsff.output, tsff.ddepth, tsff.padding, tsff.should_normalize) \
            if result == QDialog.Accepted else None


def horizontal_separator():
    result = QFrame()
    result.setFrameShape(QFrame.HLine)
    result.setFrameShadow(QFrame.Sunken)
    return result
