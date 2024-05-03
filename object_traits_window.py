from typing import Sequence

import cv2 as cv
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout, QSpinBox,
                             QDialog, QDialogButtonBox, QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox, QLabel,
                             QHBoxLayout, QListWidgetItem, QListWidget, QTabWidget, QTableWidget, QAbstractItemView,
                             QTableView, QHeaderView, QTableWidgetItem)

from error_box import ErrorBox
from forms.form_widgets.open_file_widget import OpenFileWidget
from image import ColorModes, Image
import image_traits as img_traits
from window_manager import WINDOW_MANAGER

LMIN = 0
LMAX = 255
MAX_SIZE = 256
YELLOW = (255, 220, 0)


class ObjectTraitsWindow(QMainWindow):
    def __init__(self, contours: np.ndarray | Sequence[int], parent: QMainWindow | None = None):
        super().__init__()

        WINDOW_MANAGER.add_window(self)
        self.parent_window = parent

        self.orig_image: Image = parent.image.copy()
        self.image: Image = self.orig_image.copy()

        self.contours = contours
        self.curr_cnt_idx = 0
        self.curr_cnt = contours[self.curr_cnt_idx]
        self.contours_count = len(self.contours)
        self.object_labels = [f"Object{idx}" for idx in range(self.contours_count)]

        title = "Object Traits"
        if parent is not None:
            title = f"{parent.image.name if parent.image is not None else parent.windowTitle()} | {title}"

        self.setWindowTitle(title)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        main_layout = self.layout

        top_widget = QWidget()
        top_layout = QHBoxLayout()
        top_widget.setLayout(top_layout)
        main_layout.addWidget(top_widget)

        # Preview
        preview_widget = QGroupBox()
        preview_widget.setTitle("Preview")
        preview_layout = QVBoxLayout()
        preview_widget.setLayout(preview_layout)
        top_layout.addWidget(preview_widget)

        self.image_frame = QLabel()
        self.image_frame.setMinimumSize(MAX_SIZE, MAX_SIZE)
        self.image_frame.setMaximumSize(MAX_SIZE, MAX_SIZE)
        preview_layout.addWidget(self.image_frame)

        # Object list

        self.object_list = QListWidget()

        for lbl in self.object_labels:
            QListWidgetItem(lbl, self.object_list)

        self.object_list.currentRowChanged.connect(self.curr_idx_changed)

        top_layout.addWidget(self.object_list)

        # Tabs & Tables

        self.tab_widget = QTabWidget()

        self.mom_table = QTableWidget()
        self.geom_table = QTableWidget()
        self.coeff_table = QTableWidget()
        tables = [self.mom_table, self.geom_table, self.coeff_table]

        for table in tables:
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setSelectionBehavior(QTableView.SelectRows)
            table.verticalHeader().hide()
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setColumnCount(2)

        self.mom_table.setHorizontalHeaderLabels(["Moment", "Value"])
        self.geom_table.setHorizontalHeaderLabels(["Trait", "Value"])
        self.coeff_table.setHorizontalHeaderLabels(["Coefficient", "Value"])

        self.tab_widget.addTab(self.mom_table, "Moments")
        self.tab_widget.addTab(self.geom_table, "Geometry")
        self.tab_widget.addTab(self.coeff_table, "Coefficients")

        main_layout.addWidget(self.tab_widget)

        # Post-render activities
        self.object_list.setCurrentRow(self.curr_cnt_idx)

        self.update_preview()
        self.update_tables()


        # self.setFixedSize(super().size().width() // 2 - 20, super().size().height() + 25)

    def refresh_image(self):
        self.image = self.image.colorful_contours([self.curr_cnt], True, YELLOW)

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

    def update_preview(self):
        self.image = self.orig_image.copy()
        self.refresh_image()

    def update_tables(self):
        moments = img_traits.moments(self.curr_cnt)
        geometry = {
            "Area": img_traits.area(self.curr_cnt),
            "Perimeter": img_traits.perimeter(self.curr_cnt)
        }
        coeffs = {
            "Aspect Ratio": img_traits.aspect_ratio(self.curr_cnt),
            "Extent": img_traits.extent(self.curr_cnt),
            "Solidity": img_traits.solidity(self.curr_cnt),
            "Equivalent Diameter": img_traits.equivalent_diameter(self.curr_cnt)
        }

        self.mom_table.clear()
        self.mom_table.setRowCount(len(moments))
        self.mom_table.setHorizontalHeaderLabels(["Moment", "Value"])

        self.geom_table.clear()
        self.geom_table.setRowCount(len(geometry))
        self.geom_table.setHorizontalHeaderLabels(["Trait", "Value"])

        self.coeff_table.clear()
        self.coeff_table.setRowCount(len(coeffs))
        self.coeff_table.setHorizontalHeaderLabels(["Coefficient", "Value"])

        for r, (k, v) in enumerate(moments.items()):
            self.mom_table.setItem(r, 0, QTableWidgetItem(k))
            self.mom_table.setItem(r, 1, QTableWidgetItem(str(v)))

        for r, (k, v) in enumerate(geometry.items()):
            self.geom_table.setItem(r, 0, QTableWidgetItem(k))
            self.geom_table.setItem(r, 1, QTableWidgetItem(str(v)))

        for r, (k, v) in enumerate(coeffs.items()):
            self.coeff_table.setItem(r, 0, QTableWidgetItem(k))
            self.coeff_table.setItem(r, 1, QTableWidgetItem(str(v)))

    def curr_idx_changed(self, idx):
        self.curr_cnt_idx = idx
        self.curr_cnt = self.contours[self.curr_cnt_idx]

        self.update_tables()
        self.update_preview()

    def closeEvent(self, event):
        WINDOW_MANAGER.remove_window(self)
        event.accept()
