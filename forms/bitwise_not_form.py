from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QDialog, QDialogButtonBox, QPushButton,
                             QHBoxLayout, QLabel, QLineEdit)

from error_box import ErrorBox
from forms.form_widgets.window_preview import WindowPreview
from image import Image


class BitwiseNotForm(QDialog):
    def __init__(self, callee: QMainWindow | None = None):
        super().__init__()
        self.image: Image = None
        self.result_name = "Untitled"

        title = "Bitwise NOT"
        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        images_widget = QWidget()
        images_layout = QHBoxLayout()
        images_widget.setLayout(images_layout)
        main_layout.addWidget(images_widget)

        # Intersection

        intersection_widget = QWidget()
        intersection_layout = QVBoxLayout()
        intersection_widget.setLayout(intersection_layout)
        images_layout.addWidget(intersection_widget)

        operator_label = QLabel()
        operator_label.setText("NOT")
        operator_label.setAlignment(Qt.AlignCenter)
        font = operator_label.font()
        font.setPointSize(16)
        font.setBold(True)
        operator_label.setFont(font)
        intersection_layout.addWidget(operator_label)

        refresh_button = QPushButton()
        refresh_button.setText("Refresh")
        refresh_button.pressed.connect(self.refresh_images)
        intersection_layout.addWidget(refresh_button)

        # Image

        image_widget = QWidget()
        image_layout = QVBoxLayout()
        image_widget.setLayout(image_layout)
        images_layout.addWidget(image_widget)

        im_label = QLabel()
        im_label.setText("Image")
        im_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(im_label)

        self.image_winpreview = WindowPreview()
        image_layout.addWidget(self.image_winpreview)

        # Bottom form

        name_form = QWidget()
        name_form_layout = QFormLayout()
        name_form.setLayout(name_form_layout)
        main_layout.addWidget(name_form)

        name_field = QLineEdit()
        name_field.setText("Untitled")
        name_field.textChanged.connect(self.update_name)

        name_form_layout.addRow("Name", name_field)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.update_images)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        if callee is not None:
            self.image_winpreview.set_current_window(callee)

        self.setFixedSize(self.size())

    def refresh_images(self):
        self.image_winpreview.refresh_available_windows()

    def update_images(self):
        self.image = self.image_winpreview.image

    @property
    def is_data_valid(self):
        c1 = self.image is not None
        return c1

    def update_name(self, value):
        self.result_name = value

    def accept(self):
        valid = self.is_data_valid
        if valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(callee: QMainWindow = None) -> tuple[Image, str] | None:
        bnf = BitwiseNotForm(callee)
        bnf.setModal(True)
        result = bnf.exec()
        return (bnf.image, bnf.result_name) \
            if result == QDialog.Accepted else None
