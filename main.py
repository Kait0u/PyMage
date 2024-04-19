import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from forms.range_stretch_form import RangeStretchForm

TEST = True

def test():
    import numpy as np
    from utils import bresenham
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

    image = np.zeros((64, 64))
    x1, y1, x2, y2 = randint(0, 63), randint(0, 63), randint(0, 63), randint(0, 63)
    x1, y1, x2, y2 = 0, 0, 63, 15
    print(x1, y1)
    print(x2, y2)
    line = bresenham(x1, y1, x2, y2)
    print(line)
    line = list(line)
    for p in line:
        image[p[0], p[1]] = 1
    plt.imshow(image)
    plt.show()


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
