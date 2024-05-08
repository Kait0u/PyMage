from PyQt5.QtWidgets import QMainWindow, QWidget
from sqids import Sqids

class WindowManager:
    def __init__(self):
        self._windows = []
        self._sqids = Sqids()

    def add_window(self, window: QMainWindow | QWidget):
        self._windows.append(window)

    def get_all_of_class(self, class_name: type) -> list[type]:
        result = [window for window in self._windows if isinstance(window, class_name)]
        return result

    def remove_window(self, window: QMainWindow | QWidget) -> None:
        self._windows.remove(window)

    def remove_all(self):
        self._windows.clear()

    def generate_uid(self, window: QWidget):
        win_id = [id(window)]
        return self._sqids.encode(win_id)

    @property
    def window_count(self):
        return len(self._windows)


WINDOW_MANAGER = WindowManager()
