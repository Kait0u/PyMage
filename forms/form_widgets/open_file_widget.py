import os

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QFileDialog


class OpenFileWidget(QWidget):
    def __init__(self, initial_path: str = ""):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.path = initial_path

        self.path_field = QLineEdit()
        layout.addWidget(self.path_field)

        self.open_button = QPushButton("Open File")
        self.open_button.clicked.connect(self.open_image_gsc)
        layout.addWidget(self.open_button)

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
        if path is not None and len(path) > 0 and os.path.exists(path):
            self.path = path
            self.path_field.setText(path)

    @property
    def valueChanged(self):
        return self.path_field.textChanged
