from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)


class OtsuForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.inv = False

        title = "Otsu"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Otsu"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.inv_checkbox = QCheckBox()
        self.inv_checkbox.setTristate(False)
        self.inv_checkbox.setChecked(self.inv)
        self.inv_checkbox.stateChanged.connect(self.inv_toggled)
        form_layout.addRow("Inverted", self.inv_checkbox)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    @property
    def is_data_valid(self):
        return True

    def inv_toggled(self, val):
        self.inv = self.inv_checkbox.isChecked()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> bool | None:
        of = OtsuForm(parent)
        of.setModal(True)
        result = of.exec()
        return of.inv \
            if result == QDialog.Accepted else None
