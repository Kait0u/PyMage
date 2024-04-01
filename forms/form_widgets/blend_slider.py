import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QVBoxLayout, QLabel, QSlider

MAX_VALUE = 1000


class BlendSlider(QWidget):
    def __init__(self):
        super().__init__()
        self._alpha = 0.5
        self._beta = 0.5

        layout = QVBoxLayout()
        self.setLayout(layout)

        info_widget = QWidget()
        info_layout = QHBoxLayout()
        layout.addWidget(info_widget)
        info_widget.setLayout(info_layout)

        self.alpha_label = QLabel()
        self.alpha_label.setText(self.alpha_text)
        self.alpha_label.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(self.alpha_label)

        self.beta_label = QLabel()
        self.beta_label.setText(self.beta_text)
        self.beta_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.beta_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setSingleStep(1)
        self.slider.setMaximum(MAX_VALUE)
        self.slider.setValue(MAX_VALUE // 2)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value
        self._beta = 1.0 - value

    @property
    def alpha_text(self):
        return f"α = {self.alpha:.3f}"

    @property
    def beta_text(self):
        return f"β = {self.beta:.3f}"

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value
        self._alpha = 1.0 - value

    def slider_changed(self, value):
        value /= MAX_VALUE
        self.alpha = value
        self.alpha_label.setText(self.alpha_text)
        self.beta_label.setText(self.beta_text)
