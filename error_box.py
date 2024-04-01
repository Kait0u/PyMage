from PyQt5.QtWidgets import QMessageBox, QApplication


class ErrorBox(QMessageBox):
    def __init__(self, message: str | Exception, modal: bool = True, show: bool = True):
        super().__init__()
        self.setIcon(QMessageBox.Critical)
        self.setWindowTitle("Error!")
        if isinstance(message, Exception):
            message = str(message)
        self.setText(message)
        self.setModal(modal)
        self.setStandardButtons(QMessageBox.Ok)

        if show:
            self.show()
            self.exec()

