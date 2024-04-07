from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QDialog, QDialogButtonBox, QPushButton,
                             QHBoxLayout, QLabel, QLineEdit,
                             QSlider)

from error_box import ErrorBox
from forms.form_widgets.blend_slider import BlendSlider
from forms.form_widgets.window_preview import WindowPreview
from image import Image

LMAX = 255

class BlendForm(QDialog):
    def __init__(self, callee: QMainWindow | None = None):
        super().__init__()
        self.image1: Image = None
        self.image2: Image = None
        self.alpha = 0.5
        self.beta = 0.5
        self.gamma = 0
        self.result_name = "Untitled"

        title = "Image Blend"
        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        images_widget = QWidget()
        images_layout = QHBoxLayout()
        images_widget.setLayout(images_layout)
        main_layout.addWidget(images_widget)

        # Image 1

        image1_widget = QWidget()
        image1_layout = QVBoxLayout()
        image1_widget.setLayout(image1_layout)
        images_layout.addWidget(image1_widget)

        im1_label = QLabel()
        im1_label.setText("Image 1")
        im1_label.setAlignment(Qt.AlignCenter)
        image1_layout.addWidget(im1_label)

        self.image1_winpreview = WindowPreview()
        image1_layout.addWidget(self.image1_winpreview)

        # Intersection

        intersection_widget = QWidget()
        intersection_layout = QVBoxLayout()
        intersection_widget.setLayout(intersection_layout)
        images_layout.addWidget(intersection_widget)

        operator_label = QLabel()
        operator_label.setText("⨹")
        operator_label.setAlignment(Qt.AlignCenter)
        font = operator_label.font()
        font.setPointSize(48)
        font.setBold(True)
        operator_label.setFont(font)
        intersection_layout.addWidget(operator_label)

        swap_button = QPushButton()
        swap_button.setText("⇄")
        font = swap_button.font()
        font.setPointSize(16)
        swap_button.setFont(font)
        swap_button.pressed.connect(self.swap_images)
        intersection_layout.addWidget(swap_button)

        intersection_layout.addSpacing(50)

        self.ab_slider = BlendSlider()
        intersection_layout.addWidget(self.ab_slider)

        gamma_widget = QWidget()
        gamma_layout = QVBoxLayout()
        gamma_widget.setLayout(gamma_layout)
        intersection_layout.addWidget(gamma_widget)

        self.gamma_label = QLabel()
        self.gamma_label.setText(self.gamma_text)
        self.gamma_label.setAlignment(Qt.AlignCenter)
        gamma_layout.addWidget(self.gamma_label)

        self.gamma_slider = QSlider(Qt.Horizontal)
        self.gamma_slider.setMinimum(-LMAX)
        self.gamma_slider.setMaximum(LMAX)
        self.gamma_slider.setSingleStep(1)
        self.gamma_slider.setValue(self.gamma)
        self.gamma_slider.valueChanged.connect(self.update_gamma)
        gamma_layout.addWidget(self.gamma_slider)

        # Image 2

        image2_widget = QWidget()
        image2_layout = QVBoxLayout()
        image2_widget.setLayout(image2_layout)
        images_layout.addWidget(image2_widget)

        im2_label = QLabel()
        im2_label.setText("Image 2")
        im2_label.setAlignment(Qt.AlignCenter)
        image2_layout.addWidget(im2_label)

        self.image2_winpreview = WindowPreview()
        image2_layout.addWidget(self.image2_winpreview)

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
        self.button_box.accepted.connect(self.update_weights)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        if callee is not None:
            self.image1_winpreview.set_current_window(callee)

    def refresh_images(self):
        self.image1_winpreview.refresh_available_windows()
        self.image2_winpreview.refresh_available_windows()

    def swap_images(self):
        imwin1 = self.image1_winpreview.curr_image_window
        imwin2 = self.image2_winpreview.curr_image_window
        self.image1_winpreview.set_current_window(imwin2)
        self.image2_winpreview.set_current_window(imwin1)

    @property
    def gamma_text(self):
        return f"γ = {self.gamma}"

    def update_gamma(self, value):
        self.gamma = value
        self.gamma_label.setText(self.gamma_text)

    def update_images(self):
        self.image1 = self.image1_winpreview.image
        self.image2 = self.image2_winpreview.image

    def update_weights(self):
        self.alpha = self.ab_slider.alpha
        self.beta = self.ab_slider.beta

    @property
    def is_data_valid(self):
        c1 = self.image1 is not None
        c2 = self.image2 is not None
        c3 = self.same_color()
        c4 = self.same_size()
        c5 = round(self.alpha + self.beta, 5) == 1.0
        return c1 and c2 and c3 and c4 and c5

    def same_color(self):
        if self.image1.is_gray == self.image2.is_gray:
            return True
        ErrorBox("Incompatible images. Color type mismatch.")
        return False

    def same_size(self):
        if self.image1.img.shape[:2] == self.image2.img.shape[:2]:
            return True
        ErrorBox("Incompatible images. Size mismatch.")
        return False

    def update_name(self, value):
        self.result_name = value

    def accept(self):
        valid = self.is_data_valid
        if valid: super().accept()
        else: ErrorBox("Invalid data")

    @staticmethod
    def show_dialog(callee: QMainWindow = None) -> tuple[Image, Image, float, float, int, str] | None:
        bf = BlendForm(callee)
        bf.setModal(True)
        result = bf.exec()
        return (bf.image1, bf.image2, bf.alpha, bf.beta, bf.gamma, bf.result_name) \
            if result == QDialog.Accepted else None
