import os.path

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QMenuBar, QAction, QMessageBox, QFileDialog

import image_arithmetic
from error_box import ErrorBox
from image_utils import parse_binary_rle
from image_window import ImageWindow
from window_manager import WINDOW_MANAGER


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyMage")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setFixedSize(360, 130)

        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # File menu actions
        open_gsc_action = QAction("&Open (Grayscale)", self)
        open_gsc_action.setShortcut("Ctrl+Shift+O")
        open_gsc_action.triggered.connect(self.open_image_gsc)

        open_color_action = QAction("&Open (Color)", self)
        open_color_action.triggered.connect(self.open_image_color)
        open_color_action.setShortcut("Ctrl+O")

        open_rle_action = QAction("Open (RLE)", self)
        open_rle_action.triggered.connect(self.open_image_rle)


        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.quit)
        exit_action.setStatusTip("Exits the application")

        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.addAction(open_gsc_action)
        self.file_menu.addAction(open_color_action)
        self.file_menu.addAction(open_rle_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(exit_action)

        self.arithmetic_menu = self.menu_bar.addMenu("Arithmetic")

        add_action = QAction("Add", self)
        add_action.triggered.connect(lambda: attempt(image_arithmetic.add_image))
        self.arithmetic_menu.addAction(add_action)

        sub_action = QAction("Subtract", self)
        sub_action.triggered.connect(lambda: attempt(image_arithmetic.subtract_image))
        self.arithmetic_menu.addAction(sub_action)

        blend_action = QAction("Blend", self)
        blend_action.triggered.connect(lambda: attempt(image_arithmetic.blend_image))
        self.arithmetic_menu.addAction(blend_action)

        self.arithmetic_menu.addSeparator()

        and_action = QAction("AND", self)
        and_action.triggered.connect(lambda: attempt(image_arithmetic.bitwise_and_image))
        self.arithmetic_menu.addAction(and_action)

        or_action = QAction("OR", self)
        or_action.triggered.connect(lambda: attempt(image_arithmetic.bitwise_or_image))
        self.arithmetic_menu.addAction(or_action)

        xor_action = QAction("XOR", self)
        xor_action.triggered.connect(lambda: attempt(image_arithmetic.bitwise_xor_image))
        self.arithmetic_menu.addAction(xor_action)

        not_action = QAction("NOT", self)
        not_action.triggered.connect(lambda: attempt(image_arithmetic.bitwise_not_image))
        self.arithmetic_menu.addAction(not_action)

        # About

        about_action = QAction("&About", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.about)
        self.about_menu = self.menu_bar.addAction(about_action)

    def quit(self):
        should_close = WINDOW_MANAGER.window_count == 0

        if not should_close:
            confirmation_box = QMessageBox
            answer = confirmation_box.question(self,
                                               "Quit", "Are you sure you want to quit?\nUnsaved changes will be lost!",
                                               confirmation_box.Yes | confirmation_box.No
                                               )
            should_close = answer == confirmation_box.Yes

        if should_close:
            self.close()

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

    def open_file_dialog(self, filters):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        dlg.setFileMode(QFileDialog.ExistingFile)

        dlg.setNameFilters(filters)
        dlg.selectNameFilter(filters[0])

        dlg.exec()

        result = dlg.selectedFiles()
        if len(result) > 0 and dlg.result() == QFileDialog.Accepted:
            result = result[0]
            return result
        else:
            return None

    def open_image_gsc(self):
        filters = [
            "Supported Graphics Files (*.bmp *.png *.jpg *.jpeg)",
            "BMP Files (*.bmp)",
            "JPG Files (*.jpg *.jpeg)",
            "PNG Files (*.png)",
        ]

        try:
            path = self.open_file_dialog(filters)
            if path is not None:
                imgwin = ImageWindow.from_path(path, True)
                imgwin.show()
        except Exception as e:
            ErrorBox("Something went wrong!")

    def open_image_color(self):
        filters = [
            "Supported Graphics Files (*.bmp *.png *.jpg *.jpeg)",
            "BMP Files (*.bmp)",
            "JPG Files (*.jpg *.jpeg)",
            "PNG Files (*.png)",
        ]

        try:
            path = self.open_file_dialog(filters)
            if path is not None:
                imgwin = ImageWindow.from_path(path, False)
                imgwin.show()
        except Exception as e:
            ErrorBox("Something went wrong!")

    def open_image_rle(self):
        filters = [
            "Any files (*.*)"
        ]

        try:
            path = self.open_file_dialog(filters)
            if path is not None:
                with open(path, "rb") as f:
                    rle_bytes = bytearray(f.read())
                rle_img = parse_binary_rle(rle_bytes)
                name, _ = os.path.splitext(os.path.basename(path))
                imgwin = ImageWindow.from_numpy(rle_img, name)
                imgwin.show()
        except Exception as e:
            ErrorBox("Something went wrong!")


def attempt(f):
    try:
        f()
    except Exception as error:
        ErrorBox(error)
