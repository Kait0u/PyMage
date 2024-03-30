from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)

class CannyForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.threshold1 = 100
        self.threshold2 = 200

        title = "Canny"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Canny"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.th1_spin_box = QSpinBox()
        self.th1_spin_box.setMinimum(0)
        self.th1_spin_box.setMaximum(255)
        self.th1_spin_box.setValue(self.threshold1)
        self.th1_spin_box.valueChanged.connect(self.th1_value_changed)
        form_layout.addRow("Threshold 1", self.th1_spin_box)

        self.th2_spin_box = QSpinBox()
        self.th2_spin_box.setMinimum(0)
        self.th2_spin_box.setMaximum(255)
        self.th2_spin_box.setValue(self.threshold2)
        self.th2_spin_box.valueChanged.connect(self.th2_value_changed)
        form_layout.addRow("Threshold 2", self.th2_spin_box)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    @property
    def is_data_valid(self):
        c1 = 0 <= self.threshold1 <= self.threshold2
        c2 = 0 <= self.threshold2 <= 255
        return c1 and c2

    def th1_value_changed(self, val):
        self.threshold1 = val

    def th2_value_changed(self, val):
        self.threshold2 = val

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[int, int] | None:
        cf = CannyForm(parent)
        cf.setModal(True)
        result = cf.exec()
        return (cf.threshold1, cf.threshold2) \
            if result == QDialog.Accepted else None


