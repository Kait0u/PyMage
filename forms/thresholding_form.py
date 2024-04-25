from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox)


class ThresholdingForm(QDialog):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__()
        self.threshold = 255 // 2
        self.inv = False

        title = "Thresholding"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | Thresholding"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        form_widget = QWidget()
        form_layout = QFormLayout()
        form_widget.setLayout(form_layout)
        main_layout.addWidget(form_widget)

        self.th_spin_box = QSpinBox()
        self.th_spin_box.setMinimum(0)
        self.th_spin_box.setMaximum(255)
        self.th_spin_box.setValue(self.threshold)
        self.th_spin_box.valueChanged.connect(self.th_value_changed)
        form_layout.addRow("Threshold", self.th_spin_box)

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
        c1 = 0 <= self.threshold <= 255
        return c1

    def th_value_changed(self, val):
        self.threshold = val

    def inv_toggled(self, val):
        self.inv = self.inv_checkbox.isChecked()

    def accept(self):
        if self.is_data_valid: super().accept()
        else: print("Invalid data")

    @staticmethod
    def show_dialog(parent=None) -> tuple[int, bool] | None:
        tf = ThresholdingForm(parent)
        tf.setModal(True)
        result = tf.exec()
        return (tf.threshold, tf.inv) \
            if result == QDialog.Accepted else None


