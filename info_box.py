from PyQt5.QtWidgets import QMessageBox


class InfoBox(QMessageBox):
    def __init__(self, title: str = "Info", message: str = "", modal: bool = True, show: bool = True):
        super().__init__()
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle(title)
        self.setText(message)
        self.setModal(modal)
        self.setStandardButtons(QMessageBox.Ok)

        if show:
            self.show()
            self.exec()

