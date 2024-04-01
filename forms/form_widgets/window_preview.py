from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox

from error_box import ErrorBox
from image import ColorModes, Image
from window_manager import WINDOW_MANAGER
from image_window import ImageWindow

MAX_SIZE = 256


class WindowPreview(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.image_windows: list[ImageWindow] = WINDOW_MANAGER.get_all_of_class(ImageWindow)

        try:
            self.curr_image_window: ImageWindow = self.image_windows[0]
            self.image: Image = self.curr_image_window.image
        except IndexError:
            raise Exception("No image window is open!")

        self.image_frame = QLabel()
        self.image_frame.setMinimumSize(MAX_SIZE, MAX_SIZE)
        self.image_frame.setMaximumSize(MAX_SIZE, MAX_SIZE)
        layout.addWidget(self.image_frame)

        self.image_window_combobox = QComboBox()
        self.image_window_combobox.addItems(list(map(str, self.image_windows)))
        self.image_window_combobox.currentIndexChanged.connect(self.update_curr_window)
        layout.addWidget(self.image_window_combobox)

        self.refresh_image()

    def refresh_image(self):
        color_format = QImage.Format_RGB888 if self.image.color_mode != ColorModes.GRAY else QImage.Format_Grayscale8

        qt_image = QImage(self.image.img, self.image.width,
                          self.image.height, self.image.img.strides[0], color_format)

        w = self.image.width
        h = self.image.height

        if w > h:
            ratio = h / w
            w = MAX_SIZE
            h = int(MAX_SIZE * ratio)
        else:
            ratio = w / h
            h = MAX_SIZE
            w = int(MAX_SIZE * ratio)

        qt_image = QPixmap.fromImage(qt_image).scaled(w, h)
        self.image_frame.setPixmap(qt_image)
        self.image_frame.setAlignment(Qt.AlignCenter)

    def update_curr_window(self, idx):
        try:
            self.curr_image_window = self.image_windows[idx]
            self.image = self.curr_image_window.image
            self.refresh_image()
        except Exception as error:
            ErrorBox(error)

    def refresh_available_windows(self):
        self.image_windows: list[ImageWindow] = WINDOW_MANAGER.get_all_of_class(ImageWindow)
        try:
            self.image_window_combobox.clear()
            self.image_window_combobox.addItems(list(map(str, self.image_windows)))
            self.image_window_combobox.setCurrentIndex(0)
            self.refresh_image()
        except IndexError as error:
            ErrorBox("No image window is open!")
            self.close()
        except Exception as error:
            ErrorBox(error)

    def set_current_window(self, window: ImageWindow):
        if window in self.image_windows:
            idx = self.image_windows.index(window)
            self.image_window_combobox.setCurrentIndex(idx)
            self.refresh_image()
