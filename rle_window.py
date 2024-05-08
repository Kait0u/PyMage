import os

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QGroupBox, QTableView, QAbstractItemView, \
    QTableWidgetItem, QHeaderView, QPushButton, QFileDialog

from error_box import ErrorBox
from image import Image
from image_utils import make_binary_rle
from info_box import InfoBox
from window_manager import WINDOW_MANAGER


class RLEWindow(QMainWindow):
    def __init__(self, image: Image, parent: QMainWindow | None = None):
        super().__init__()
        WINDOW_MANAGER.add_window(self)
        self.parent_window = parent
        self.image = image

        title = "RLE"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | {title}"

        self.setWindowTitle(title)

        self.widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table_group = QGroupBox("Data")
        self.layout.addWidget(self.table_group)
        self.table_group_layout = QVBoxLayout()
        self.table_group.setLayout(self.table_group_layout)
        self.layout.addWidget(self.table_group)

        self.data_table = QTableWidget()
        self.table_group_layout.addWidget(self.data_table)

        self.data_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.data_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.data_table.setSelectionBehavior(QTableView.SelectRows)

        self.data_table.setColumnCount(2) # 2: name and value
        self.data_table.verticalHeader().hide()
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.save_button = QPushButton("SAVE RLE")
        self.save_button.clicked.connect(self.save_rle)
        self.layout.addWidget(self.save_button)

        # Post-render activities

        self.rle = self.image.rle_encode_img()
        self.rle_vals = np.array([pair[0] for pair in self.rle], dtype=np.uint8)
        self.rle_counts = np.array([pair[1] for pair in self.rle], dtype=np.uint32)
        self.rle_header = np.array([self.image.height, self.image.width], dtype=np.uint32)

        self.size_bytes = self.image.size_bytes
        self.rle_size_bytes = self.rle_vals.nbytes + self.rle_counts.nbytes
        self.rleh_size_bytes = self.rle_header.nbytes + self.rle_size_bytes
        self.level_of_compression = self.size_bytes / self.rle_size_bytes

        self.generate_table()
        self.setFixedSize(self.size().width() // 2, self.size().width() // 2)

    def generate_table(self):
        self.data_table.clear()
        self.data_table.setHorizontalHeaderLabels(["Property", "Value"])

        data = [
            ("Uncompressed Size (B)", self.size_bytes),
            ("RLE-Compressed Size (B)", self.rle_size_bytes),
            ("RLE-Compressed Size + Headers (B)", self.rleh_size_bytes),
            ("Level of Compression", f"{self.level_of_compression:.3f}")
        ]

        size = len(data)
        self.data_table.setRowCount(size)

        for idx in range(size):
            self.data_table.setItem(idx, 0, QTableWidgetItem(str(data[idx][0])))
            self.data_table.setItem(idx, 1, QTableWidgetItem(str(data[idx][1])))

        self.data_table.update()

    def closeEvent(self, event):
        WINDOW_MANAGER.remove_window(self)
        event.accept()

    def _save_file_dialog(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setFileMode(QFileDialog.AnyFile)

        filters = [
            "All Files (*)"
        ]

        dlg.setNameFilters(filters)

        file_name, ext = os.path.splitext(self.image.name)

        dlg.selectNameFilter(filters[-1])
        dlg.setDefaultSuffix("")
        dlg.selectFile(file_name)

        dlg.exec()

        result = dlg.selectedFiles()
        if len(result) > 0 and dlg.result() == QFileDialog.Accepted:
            result = result[0]
            return result
        else:
            return None

    def save_rle(self):
        try:
            binary_rle = make_binary_rle(self.rle, int(self.image.height), int(self.image.width))
        except Exception as e:
            ErrorBox(e)

        try:
            path = self._save_file_dialog()
            if path is not None:
                with open(path, "wb") as binfile:
                    binfile.write(binary_rle)
                InfoBox("File saved successfully!")
        except Exception as e:
            ErrorBox("Something went wrong!")

