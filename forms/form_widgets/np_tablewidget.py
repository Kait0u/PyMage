import numpy as np
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
from PyQt5.QtCore import Qt


class NpTableWidget(QTableWidget):
    def __init__(self, data: np.ndarray, hide_headers=True, hide_scrollbars=True, can_select=False, can_edit=False, parent=None):
        super(NpTableWidget, self).__init__(parent)
        self._data = data
        self.setRowCount(data.shape[0])
        self.setColumnCount(data.shape[1])
        if hide_headers:
            self.horizontalHeader().hide()
            self.verticalHeader().hide()
        if hide_scrollbars:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        if not can_select:
            self.setSelectionMode(QAbstractItemView.NoSelection)
        if not can_edit:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.update_data()

    @staticmethod
    def empty_editable(width: int, height: int) -> "NpTableWidget":
        data = np.empty((width, height))
        new_widget = NpTableWidget(data, can_edit=True)
        return new_widget

    @property
    def data(self) -> np.ndarray:
        return self._data

    @data.setter
    def data(self, value):
        self.update_data(value)

    def update_data(self, data: np.ndarray | None = None):
        self.clear()
        if data is not None:
            self._data = data

        r = self._data.shape[0]
        c = self._data.shape[1]

        if data is not None:
            self.setRowCount(r)
            self.setColumnCount(c)

        for idx_r in range(r):
            for idx_c in range(c):
                item = QTableWidgetItem()
                item.setText(str(self._data[idx_r, idx_c]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(idx_r, idx_c, item)

    def extract_numpy(self, dtype: np.dtype):
        r = self.rowCount()
        c = self.columnCount()

        data = np.zeros((r, c), dtype=dtype)

        for idx_r in range(r):
            for idx_c in range(c):
                try:
                    item = self.item(idx_r, idx_c).text()
                    data[idx_r, idx_c] = item
                except Exception as error:
                    print(error)
                    return

        return data

