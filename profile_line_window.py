import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QGroupBox, QTableView, QAbstractItemView, QTableWidgetItem, QHeaderView

from image import Image
from widgets.mplcanvas import MplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from window_manager import WINDOW_MANAGER


class ProfileLineWindow(QMainWindow):
    def __init__(self, image: Image, line_points: np.ndarray, parent: QMainWindow | None = None):
        super().__init__()
        WINDOW_MANAGER.add_window(self)
        self.parent_window = parent
        self.image = image
        self.points = [tuple(p) for p in line_points]
        self.luminosities = [image.img[x, y] for (x, y) in self.points]
        self.distances = np.arange(len(self.points))

        self.xmin = min(self.points, key=lambda x: x[0])[0]
        self.xmax = max(self.points, key=lambda x: x[0])[0]
        self.ymin = 0
        self.ymax = 255

        self.widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.plot_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        # self.plot_canvas.axes.format_coord = lambda x, y: \
        #     f"X = {max(np.int16(np.floor(x)), 0)}\nY = {self.histogram.array[max(0, np.int16(np.floor(x)))]}"
        self.plot_navi = NavigationToolbar(self.plot_canvas, self)

        self.layout.addWidget(self.plot_navi)
        self.layout.addWidget(self.plot_canvas)

        self.table_group = QGroupBox("Table")
        self.layout.addWidget(self.table_group)
        self.table_group_layout = QVBoxLayout()
        self.table_group.setLayout(self.table_group_layout)

        self.profile_table = QTableWidget()
        self.table_group_layout.addWidget(self.profile_table)

        self.profile_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.profile_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.profile_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.profile_table.setSelectionBehavior(QTableView.SelectRows)

        self.profile_table.setColumnCount(3) # 3: pixel coordinates (2) and value
        self.profile_table.verticalHeader().hide()
        self.profile_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.update_display()

    def draw(self):
        self.plot_canvas.axes.clear()
        self.plot_canvas.figure.tight_layout(pad=2)
        self.plot_canvas.axes.set_title(self.image.name)
        self.plot_canvas.axes.set_xlabel("Distance (px)")
        self.plot_canvas.axes.set_ylabel("Brightness")
        self.plot_canvas.axes.set_xlim(self.distances[0] - 0.5, self.distances[-1] + 0.5)
        self.plot_canvas.axes.set_ylim(self.ymin, self.ymax + 0.5)

        x = self.distances
        y = self.luminosities

        self.plot_canvas.axes.plot(x, y, color="black")

        self.plot_canvas.draw()

    def generate_table(self):
        self.profile_table.clear()
        self.profile_table.setHorizontalHeaderLabels(["X", "Y", "Luminosity"])

        size = self.xmax - self.xmin + 1
        self.profile_table.setRowCount(size)

        for idx in range(size):
            self.profile_table.setItem(idx, 0, QTableWidgetItem(str(self.points[idx][0])))
            self.profile_table.setItem(idx, 1, QTableWidgetItem(str(self.points[idx][1])))
            self.profile_table.setItem(idx, 2, QTableWidgetItem(str(self.luminosities[idx])))

        self.profile_table.update()

    def update_display(self):
        self.generate_table()
        self.draw()
        self.update()

    def closeEvent(self, event):
        self.parent_window.histogram_window = None
        WINDOW_MANAGER.remove_window(self)
        event.accept()

    def resizeEvent(self, event):
        self.draw()
