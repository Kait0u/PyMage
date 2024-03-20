import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSpacerItem, QTableWidget, QGroupBox, QScrollArea, \
    QTableView, QAbstractItemView, QTableWidgetItem, QHeaderView

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg \
    import (FigureCanvasQTAgg as FigureCanvas,
            NavigationToolbar2QT as NavigationToolbar)

from window_manager import WINDOW_MANAGER


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class HistogramWindow(QMainWindow):
    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent_window = parent
        self.update_data(False)

        self.widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.plot_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.plot_navi = NavigationToolbar(self.plot_canvas, self)

        self.layout.addWidget(self.plot_navi)
        self.layout.addWidget(self.plot_canvas)

        self.table_group = QGroupBox("Table")
        self.layout.addWidget(self.table_group)
        self.table_group_layout = QVBoxLayout()
        self.table_group.setLayout(self.table_group_layout)

        self.hist_table = QTableWidget()
        self.table_group_layout.addWidget(self.hist_table)

        self.hist_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.hist_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.hist_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.hist_table.setSelectionBehavior(QTableView.SelectRows)
        self.hist_table.setColumnCount(2)  # 2 because there's a pixel value and the number of times it appeared
        self.hist_table.verticalHeader().hide()
        self.hist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.update_display()
        self.hist_table.cellActivated.connect(self.cell_selected)

    def draw(self, highlight_idx=None):
        self.plot_canvas.axes.clear()
        self.plot_canvas.axes.set_title(self.image.name)
        self.plot_canvas.axes.set_xlim(self.histogram.min - 1, self.histogram.max)
        self.plot_canvas.axes.set_ylim(0, int(np.max(self.histogram.array) * 1.1))

        x = np.arange(self.histogram.min, self.histogram.max + 1)
        y = self.histogram.hist_array

        self.bars = self.plot_canvas.axes.bar(x, y, color="black", align='center', width=1.0)
        if highlight_idx is not None: self.bars[highlight_idx].set_color("red")

        self.plot_canvas.draw()

    def generate_table(self):
        self.hist_table.clear()
        self.hist_table.setHorizontalHeaderLabels(["Brightness", "Count"])
        size = self.histogram.array.size
        hmin = self.histogram.min
        arr = self.histogram.array
        self.hist_table.setRowCount(size)

        for idx in range(size):
            self.hist_table.setItem(idx, 0, QTableWidgetItem(str(hmin + idx)))
            self.hist_table.setItem(idx, 1, QTableWidgetItem(str(arr[idx])))

        self.hist_table.update()

    def update_data(self, update_display: bool = True):
        self.image = self.parent_window.image
        self.histogram = self.image.histogram
        self.setWindowTitle(f"Histogram: {self.image.name}")

        if update_display: self.update_display()

    def update_display(self):
        self.generate_table()
        self.draw()
        self.update()

    def cell_selected(self, r, c):
        self.draw(r)

    def closeEvent(self, event):
        self.parent_window.histogram_window = None
        WINDOW_MANAGER.remove_window(self)
