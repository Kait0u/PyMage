import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from forms.range_stretch_form import RangeStretchForm

TEST = False

def test():
    import numpy as np
    from utils import bresenham, rhombus_ones
    from random import randint
    import matplotlib.pyplot as plt
    from image import Image, ColorModes


    p = r"C:\Users\jjaw-\Downloads\harold.jpg"
    # p = r"C:\Users\jjaw-\Downloads\lena.png"

    im = Image.from_file(p)

    b = bresenham(0, 5, 12, 25)
    for el in b:
        x, y = el[0], el[1]
        print(im.img[x, y])


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    if not TEST:
        main()
    else:
        test()
