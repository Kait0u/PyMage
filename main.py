import sys
from sys import argv

from PyQt5.QtWidgets import QApplication

from image import Image, ColorModes
import cv2 as cv

# from image_window import ImageWindow
from main_window import MainWindow
from range_stretch_form import RangeStretchForm


def test():
    p = r"C:\Users\jjaw-\Downloads\harold.jpg"
    # p = r"C:\Users\jjaw-\Downloads\lena.png"

    app = QApplication(sys.argv)
    rsf = RangeStretchForm()
    rsf.show()
    # print(rsf.p1)
    app.exec()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
    # test()
