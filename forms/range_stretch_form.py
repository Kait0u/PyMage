import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QSpinBox,
                             QDialog, QDialogButtonBox)

from mplcanvas import MplCanvas

LMIN = 0
LMAX = 255


class RangeStretchForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.p1 = LMIN
        self.p2 = LMAX
        self.q3 = LMIN
        self.q4 = LMAX
        self.lut = np.arange(self.p1, self.p2 + 1, 1, dtype=np.uint8)

        title = "Stretch Range"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Stretch Range"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.plot_canvas = MplCanvas(self, width=4, height=4, dpi=100)
        main_layout.addWidget(self.plot_canvas)

        form_widget = QWidget()
        form_layout = QHBoxLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        left_form = QWidget()
        left_form_layout = QFormLayout()
        left_form.setLayout(left_form_layout)
        form_layout.addWidget(left_form)

        self.p1_spin_box = create_spin_box()
        self.p1_spin_box.valueChanged.connect(self.p1_value_changed)
        self.p2_spin_box = create_spin_box(curr_val=LMAX)
        self.p2_spin_box.valueChanged.connect(self.p2_value_changed)

        left_form_layout.addRow("p1", self.p1_spin_box)
        left_form_layout.addRow("p2", self.p2_spin_box)

        right_form = QWidget()
        right_form_layout = QFormLayout()
        right_form.setLayout(right_form_layout)
        form_layout.addWidget(right_form)

        self.q3_spin_box = create_spin_box()
        self.q3_spin_box.valueChanged.connect(self.q3_value_changed)
        self.q4_spin_box = create_spin_box(curr_val=LMAX)
        self.q4_spin_box.valueChanged.connect(self.q4_value_changed)

        right_form_layout.addRow("q3", self.q3_spin_box)
        right_form_layout.addRow("q4", self.q4_spin_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.update_data()

    def recalculate_lut(self):
        self.lut = np.arange(LMIN, LMAX + 1, 1, dtype=np.uint8)
        new_slice = np.floor(np.linspace(self.q3, self.q4, self.p2 - self.p1 + 1, True))
        self.lut[self.p1 : self.p2 + 1] = new_slice

    def draw_plot(self):
        self.plot_canvas.axes.clear()

        x = np.arange(LMIN, LMAX + 1, 1, dtype=np.uint8)
        y = self.lut
        tick_step = 20

        self.plot_canvas.axes.set_title("Preview")
        self.plot_canvas.axes.plot(x, y)
        self.plot_canvas.axes.plot([self.p1, self.p2], [self.q3, self.q4], marker='*', linestyle="", markersize=8)
        self.plot_canvas.axes.set_xlim(LMIN, LMAX)
        self.plot_canvas.axes.set_xticks(np.append(np.arange(LMIN, LMAX + 1, tick_step), [LMAX]))
        self.plot_canvas.axes.tick_params(axis="x", labelrotation=90)
        self.plot_canvas.axes.set_ylim(LMIN, LMAX)
        self.plot_canvas.axes.set_yticks(np.append(np.arange(LMIN, LMAX + 1, tick_step), [LMAX]))
        self.plot_canvas.draw()

    def update_data(self):
        if self.p1 < self.p2:
            self.recalculate_lut()
            self.draw_plot()
            self.is_data_valid = True
        else:
            print("p1 must be lower than p2!")
            self.is_data_valid = False

    def p1_value_changed(self, val):
        self.p1 = val
        self.update_data()

    def p2_value_changed(self, val):
        self.p2 = val
        self.update_data()

    def q3_value_changed(self, val):
        self.q3 = val
        self.update_data()

    def q4_value_changed(self, val):
        self.q4 = val
        self.update_data()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[int, int, int, int] | None:
        rsf = RangeStretchForm(parent)
        rsf.setModal(True)
        result = rsf.exec()
        return (rsf.p1, rsf.p2, rsf.q3, rsf.q4) if result == QDialog.Accepted else None


def create_spin_box(min_val: int = LMIN, max_val: int = LMAX, curr_val: int = LMIN) -> QSpinBox:
    result = QSpinBox()
    result.setMinimum(min_val)
    result.setMaximum(max_val)
    result.setValue(curr_val)
    return result

