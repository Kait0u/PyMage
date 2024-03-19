from PyQt5.QtWidgets import QMainWindow, QWidget

class WindowManager:
    def __init__(self):
        self.windows = []

    def add_window(self, window: QMainWindow | QWidget):
        self.windows.append(window)

    def remove_window(self, window: QMainWindow | QWidget) -> None:
        self.windows.remove(window)

    def remove_all(self):
        self.windows.clear()


WINDOW_MANAGER = WindowManager()