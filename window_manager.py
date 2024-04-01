from PyQt5.QtWidgets import QMainWindow, QWidget

from image_window import ImageWindow


class WindowManager:
    def __init__(self):
        self.windows = []
        self.image_windows = []

    def add_window(self, window: QMainWindow | QWidget):
        self.windows.append(window)
        if isinstance(window, ImageWindow):
            self.image_windows.append(window)

    def remove_window(self, window: QMainWindow | QWidget) -> None:
        self.windows.remove(window)
        if isinstance(window, ImageWindow):
            self.image_windows.remove(window)

    def remove_all(self):
        self.image_windows.clear()
        self.windows.clear()
        self.image_windows.clear()


WINDOW_MANAGER = WindowManager()
