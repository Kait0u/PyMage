from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox)

from error_box import ErrorBox


class BlurForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.size = 3

        title = "Blur"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Blur"

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

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setFixedSize(super().size().width() // 4, super().size().height() // 5)

    @property
    def is_data_valid(self):
        return self.size % 2 == 1 and self.size > 2

    def size_value_changed(self, val):
        self.size = val

    def accept(self):
        if self.is_data_valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> int | None:
        bf = BlurForm(parent)
        bf.setModal(True)
        result = bf.exec()
        return bf.size if result == QDialog.Accepted else None


