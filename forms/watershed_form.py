from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)

from error_box import ErrorBox
from forms.form_widgets.separators import HorizontalSeparator


class WatershedForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.do_boundaries = True
        self.do_colors = True
        self.do_binary = True
        self.inv = True

        title = "Watershed"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Watershed"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.boundary_checkbox = QCheckBox()
        self.boundary_checkbox.setTristate(False)
        self.boundary_checkbox.setChecked(self.do_boundaries)
        self.boundary_checkbox.stateChanged.connect(self.boundary_toggle)
        form_layout.addRow("Boundaries", self.boundary_checkbox)

        self.colors_checkbox = QCheckBox()
        self.colors_checkbox.setTristate(False)
        self.colors_checkbox.setChecked(self.do_colors)
        self.colors_checkbox.stateChanged.connect(self.colors_toggle)
        form_layout.addRow("Colors", self.colors_checkbox)

        self.binary_checkbox = QCheckBox()
        self.binary_checkbox.setTristate(False)
        self.binary_checkbox.setChecked(self.do_binary)
        self.binary_checkbox.stateChanged.connect(self.binary_toggle)
        form_layout.addRow("Binary", self.binary_checkbox)

        main_layout.addWidget(HorizontalSeparator())

        form_widget2 = QWidget()
        form_layout2 = QFormLayout()
        form_widget2.setLayout(form_layout2)
        main_layout.addWidget(form_widget2)

        self.inv_checkbox = QCheckBox()
        self.inv_checkbox.setTristate(False)
        self.inv_checkbox.setChecked(self.inv)
        self.inv_checkbox.stateChanged.connect(self.inv_toggle)
        form_layout2.addRow("Inverted Thresholding", self.inv_checkbox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setFixedSize(super().size().width() // 3, super().size().height() // 3 + 20)

    @property
    def is_data_valid(self):
        return True

    def boundary_toggle(self, val):
        self.do_boundaries = self.boundary_checkbox.isChecked()

    def colors_toggle(self, val):
        self.do_colors = self.colors_checkbox.isChecked()

    def binary_toggle(self, val):
        self.do_binary = self.binary_checkbox.isChecked()

    def inv_toggle(self, val):
        self.inv = self.inv_checkbox.isChecked()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[bool, bool, bool, bool] | None:
        wf = WatershedForm(parent)
        wf.setModal(True)
        result = wf.exec()
        return (wf.do_boundaries, wf.do_colors, wf.do_binary, wf.inv) \
            if result == QDialog.Accepted else None


