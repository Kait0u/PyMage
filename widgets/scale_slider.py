from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QSlider, QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QToolButton
from math import log10, floor

SCALING = [10, 25, 50, 100, 150, 200, 300, 400, 500]
DEFAULT = 100
DEFAULT_IDX = SCALING.index(DEFAULT)
MAX_DIGITS = len(str(max(SCALING)))

MAX_WIDTH = 400

class ScaleSlider(QWidget):
    def __init__(self):
        super().__init__()

        self.current_idx = DEFAULT_IDX
        ss_layout = QHBoxLayout(self)

        self.minus_button = QToolButton()
        self.minus_button.setText("-")
        self.minus_button.pressed.connect(self.decr_curr_idx)
        self.minus_button.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_Minus))
        ss_layout.addWidget(self.minus_button)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, len(SCALING) - 1)
        self.slider.setValue(self.current_idx)
        self.slider.setStyleSheet("""
            .QSlider::handle:horizontal {
                width: 5px;
                height: 10px;
                
            }
        """)
        self.slider.valueChanged.connect(self.slider_changed)

        ss_layout.addWidget(self.slider)

        self.plus_button = QToolButton()
        self.plus_button.setText("+")
        self.plus_button.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_Plus))
        self.plus_button.pressed.connect(self.incr_curr_idx)
        ss_layout.addWidget(self.plus_button)

        self.display = QLabel()
        self.display.setText(self.display_text)
        ss_layout.addWidget(self.display)

        button_size = QSize(
            max(self.plus_button.width(), self.minus_button.width()),
            max(self.plus_button.height(), self.minus_button.height()),
        )

        self.plus_button.resize(button_size)
        self.minus_button.resize(button_size)

        self.valueChanged = self.slider.valueChanged

        self.setMaximumWidth(MAX_WIDTH)

    @property
    def value(self):
        return SCALING[self.current_idx]

    @property
    def display_text(self):
        return f"{self.value: >{MAX_DIGITS}}%"

    def incr_curr_idx(self):
        incr = 1 if self.current_idx < len(SCALING) - 1 else 0
        self.slider.setValue(self.current_idx + incr)

    def decr_curr_idx(self):
        decr = 1 if self.current_idx > 0 else 0
        self.slider.setValue(self.current_idx - decr)

    def slider_changed(self, value):
        self.current_idx = value
        self.display.setText(self.display_text)
