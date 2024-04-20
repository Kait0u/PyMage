import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from forms.range_stretch_form import RangeStretchForm

TEST = True

def test():
    import numpy as np
    from utils import bresenham, rhombus_ones
    from random import randint
    import matplotlib.pyplot as plt


    p = r"C:\Users\jjaw-\Downloads\harold.jpg"
    # p = r"C:\Users\jjaw-\Downloads\lena.png"

    # app = QApplication(sys.argv)
    # from image import Image
    # img = Image.from_file(p, True)
    # img.posterize(2)
    # img = img.bitwise_not()

    # from image import Padding
    # img.skeletonize(np.ones((3, 3)), Padding.REFLECT)
    # img.show()
    # # print(rsf.p1)
    # app.exec()

    for n in range(3, 16, 2):
        r = rhombus_ones(n)
        print(r)
        plt.imshow(r)
        plt.show()
        print()


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
