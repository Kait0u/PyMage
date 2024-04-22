from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)


class PyramidForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.do_quarter = True
        self.do_half = True
        self.do_double = True
        self.do_quadruple = True

        title = "Pyramid"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Pyramid"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.quarter_checkbox = QCheckBox()
        self.quarter_checkbox.setTristate(False)
        self.quarter_checkbox.setChecked(self.do_quarter)
        self.quarter_checkbox.stateChanged.connect(self.quarter_toggle)
        form_layout.addRow("25%", self.quarter_checkbox)

        self.half_checkbox = QCheckBox()
        self.half_checkbox.setTristate(False)
        self.half_checkbox.setChecked(self.do_half)
        self.half_checkbox.stateChanged.connect(self.half_toggle)
        form_layout.addRow("50%", self.half_checkbox)

        self.double_checkbox = QCheckBox()
        self.double_checkbox.setTristate(False)
        self.double_checkbox.setChecked(self.do_double)
        self.double_checkbox.stateChanged.connect(self.double_toggle)
        form_layout.addRow("200%", self.double_checkbox)

        self.quadruple_checkbox = QCheckBox()
        self.quadruple_checkbox.setTristate(False)
        self.quadruple_checkbox.setChecked(self.do_quadruple)
        self.quadruple_checkbox.stateChanged.connect(self.quadruple_toggle)
        form_layout.addRow("400%", self.quadruple_checkbox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    @property
    def is_data_valid(self):
        return True

    def quarter_toggle(self, val):
        self.do_quarter = self.quarter_checkbox.isChecked()

    def half_toggle(self, val):
        self.do_half = self.half_checkbox.isChecked()

    def double_toggle(self, val):
        self.do_double = self.double_checkbox.isChecked()

    def quadruple_toggle(self, val):
        self.do_quadruple = self.quadruple_checkbox.isChecked()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[bool, bool, bool, bool] | None:
        pf = PyramidForm(parent)
        pf.setModal(True)
        result = pf.exec()
        return (pf.do_quarter, pf.do_half, pf.do_double, pf.do_quadruple) \
            if result == QDialog.Accepted else None


