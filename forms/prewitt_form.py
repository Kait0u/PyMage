import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QDialog, QDialogButtonBox, QComboBox,
                             QHBoxLayout, QDial, QLabel, QGraphicsView, QGraphicsScene)

from error_box import ErrorBox
from forms.form_widgets.np_tablewidget import NpTableWidget
from image import DesiredDepth, Padding
from masks.prewitt_masks import Prewitt


class PrewittForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.filter = Prewitt.N.value
        self.filter_options = [Prewitt.N, Prewitt.NE, Prewitt.E, Prewitt.SE, Prewitt.S, Prewitt.SW, Prewitt.W, Prewitt.NW]
        self.ddepth = DesiredDepth.U8
        self.ddepth_options = [DesiredDepth.U8, DesiredDepth.F64]
        self.padding = Padding.REPLICATE
        self.padding_options = [Padding.REPLICATE, Padding.ISOLATED, Padding.REFLECT]

        title = "Prewitt"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Prewitt"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.filter_table = NpTableWidget(self.filter)
        main_layout.addWidget(self.filter_table)

        right_side_widget = QWidget()
        right_side_layout = QVBoxLayout()
        right_side_widget.setLayout(right_side_layout)
        main_layout.addWidget(right_side_widget)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        right_side_layout.addWidget(form_widget)

        self.knob_box = QWidget()
        knob_box_layout = QVBoxLayout()
        self.knob_box.setLayout(knob_box_layout)

        direction_knob_wrapper = QGraphicsView()
        direction_knob_wrapper.setStyleSheet("border: 0px")
        scene = QGraphicsScene()
        direction_knob_wrapper.setScene(scene)
        knob_box_layout.addWidget(direction_knob_wrapper)

        self.direction_knob = QDial()
        self.direction_knob.setMinimum(0)
        self.direction_knob.setMaximum(len(self.filter_options))
        self.direction_knob.setValue(0)
        self.direction_knob.setWrapping(True)
        self.direction_knob.setNotchesVisible(True)
        self.direction_knob.valueChanged.connect(self.knob_position_changed)
        graphics_item = scene.addWidget(self.direction_knob)
        graphics_item.setRotation(180)

        self.direction_label = QLabel()
        self.direction_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.direction_label.setText(self.filter_options[self.direction_knob.value()].name)
        knob_box_layout.addWidget(self.direction_label)

        form_layout.addRow("Direction", self.knob_box)

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
        right_side_layout.addWidget(self.button_box)

        # self.setFixedSize(QSize(200, 300))

    @property
    def is_data_valid(self):
        c1 = self.filter in self.filter_options
        c2 = self.ddepth in self.ddepth_options
        c3 = self.padding in self.padding_options
        return c1 and c2 and c3

    def knob_position_changed(self, value):
        value %= len(self.filter_options)

        new_filter = self.filter_options[value]
        self.filter = new_filter.value
        self.direction_label.setText(new_filter.name)
        self.filter_table.data = self.filter

    def padding_idx_changed(self, idx):
        self.padding = self.padding_options[idx]

    def ddepth_idx_changed(self, idx):
        self.ddepth = self.ddepth_options[idx]

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[np.ndarray, DesiredDepth, Padding] | None:
        pf = PrewittForm(parent)
        pf.setModal(True)
        result = pf.exec()
        return (pf.filter, pf.ddepth, pf.padding) \
            if result == QDialog.Accepted else None


