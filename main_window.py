import sys
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QMenuBar, QAction, QMessageBox, QDialog, QFileDialog
from image_window import ImageWindow
from window_manager import WINDOW_MANAGER


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.subwindows = []

        self.setWindowTitle("PyMage")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setMinimumSize(360, 130)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # File menu actions
        open_gsc_action = QAction("&Open (Grayscale)", self)
        open_gsc_action.setShortcut("Ctrl+Shift+O")
        open_gsc_action.triggered.connect(self.open_image_gsc)

        open_color_action = QAction("&Open (Color)", self)
        open_color_action.triggered.connect(self.open_image_color)
        open_color_action.setShortcut("Ctrl+O")

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        exit_action.setStatusTip("Exits the application")

        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.addAction(open_gsc_action)
        self.file_menu.addAction(open_color_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exit_action)

        about_action = QAction("&About", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.about)
        self.about_menu = self.menu_bar.addAction(about_action)

    def closeEvent(self, event):
        WINDOW_MANAGER.remove_all()
        event.accept()

    def about(self):
        message = "\n".join(
            ["PyMage: Image Processing",
             "Author: Jakub Jaworski (20318, ID06IO1) [Kait0u]",
             "Overseer: Dr Eng. Łukasz Roszkowiak",
             "WIT Academy, Warsaw (2024)"
             ]
        )
        dlg = QMessageBox(self)
        dlg.setWindowTitle("About PyMage")
        dlg.setText(message)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setDefaultButton(QMessageBox.Ok)
        dlg.setIconPixmap(QPixmap("assets/icon.png"))
        dlg.exec()

    def open_file_dialog(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        dlg.setFileMode(QFileDialog.ExistingFile)

        filters = [
            "Supported Graphics Files (*.bmp *.png *.jpg *.jpeg)",
            "BMP Files (*.bmp)",
            "JPG Files (*.jpg *.jpeg)",
            "PNG Files (*.png)",
        ]
        dlg.setNameFilters(filters)
        dlg.selectNameFilter(filters[0])

        dlg.exec()

        result = dlg.selectedFiles()
        if len(result) > 0:
            result = result[0]
            return result
        else:
            return None

    def open_image_gsc(self):
        path = self.open_file_dialog()
        if path is not None:
            imgwin = ImageWindow.from_path(path, True)
            WINDOW_MANAGER.add_window(imgwin)
            # imgwin.setParent(self)
            imgwin.show()

    def open_image_color(self):
        path = self.open_file_dialog()
        if path is not None:
            imgwin = ImageWindow.from_path(path, False)
            WINDOW_MANAGER.add_window(imgwin)
            # imgwin.setParent(self)
            imgwin.show()
