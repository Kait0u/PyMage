import sys
from sys import argv

from PyQt5.QtWidgets import QApplication

from image import Image, ColorModes
import cv2 as cv

# from image_window import ImageWindow
from main_window import MainWindow


def test():
    p = r"C:\Users\jjaw-\Downloads\harold.jpg"
    # p = r"C:\Users\jjaw-\Downloads\lena.png"

    image = Image.from_file(p)
    image.convert_color(ColorModes.LAB)
    image.convert_color(ColorModes.RGB)
    image.show()

    # image.convert_color(ColorModes.GRAY)
    # # image.histogram.show()
    # # image.img //= 2
    for im in image.split_rgb():
        im.histogram.show()
        im.show()
    # # image.stretch_histogram(50, 100)
    # # image.stretch_histogram(0, 255)
    # image.histogram.show()
    # image.show()
    # image.equalize_histogram()
    # image.histogram.show()
    # image.show()

    # app = QApplication(sys.argv)
    # win = ImageWindow.from_path(p, True)
    # win.show()
    # app.exec()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
    # test()
