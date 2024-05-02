import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox)

from error_box import ErrorBox
from widgets.mplcanvas import MplCanvas

LMIN = 0
LMAX = 255


class PosterizeForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.lvls = 8
        self.lut = np.arange(LMIN, LMAX + 1, 1, dtype=np.uint8)

        title = "Posterize"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Posterize"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.plot_canvas = MplCanvas(self, width=4, height=4, dpi=100)
        main_layout.addWidget(self.plot_canvas)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.lvls_spin_box = create_spin_box(2, LMAX, self.lvls)
        self.lvls_spin_box.valueChanged.connect(self.lvls_value_changed)

        form_layout.addRow("Levels of grayness", self.lvls_spin_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.update_data()

    def recalculate_lut(self):
        length = LMAX - LMIN + 1
        bins = np.floor(np.linspace(LMIN, LMAX, self.lvls, True)).astype(np.uint8)
        per_bin = LMAX // self.lvls

        lut = []
        for idx in range(self.lvls):
            lut += per_bin * [bins[idx]]

        while len(lut) < length:
            lut.append(bins[-1])

        self.lut = np.array(lut)

    def draw_plot(self):
        self.plot_canvas.axes.clear()

        x = np.arange(LMIN, LMAX + 1, 1, dtype=np.uint8)
        y = self.lut
        tick_step = 20

        self.plot_canvas.axes.set_title("Preview")
        self.plot_canvas.axes.bar(x, self.lut, color="blue", align='center', width=1.0)
        self.plot_canvas.axes.set_xlim(LMIN, LMAX)
        self.plot_canvas.axes.set_xticks(np.append(np.arange(LMIN, LMAX + 1, tick_step), [LMAX]))
        self.plot_canvas.axes.tick_params(axis="x", labelrotation=90)
        self.plot_canvas.axes.set_ylim(LMIN, LMAX)
        self.plot_canvas.axes.set_yticks(np.append(np.arange(LMIN, LMAX + 1, tick_step), [LMAX]))
        self.plot_canvas.draw()

    def update_data(self):
        self.recalculate_lut()
        self.draw_plot()
        self.is_data_valid = True

    def lvls_value_changed(self, val):
        self.lvls = val
        self.update_data()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> int | None:
        pf = PosterizeForm(parent)
        pf.setModal(True)
        result = pf.exec()
        return pf.lvls if result == QDialog.Accepted else None


def create_spin_box(min_val: int = LMIN, max_val: int = LMAX, curr_val: int = LMIN) -> QSpinBox:
    result = QSpinBox()
    result.setMinimum(min_val)
    result.setMaximum(max_val)
    result.setValue(curr_val)
    return result

