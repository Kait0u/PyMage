import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
from forms.range_stretch_form import RangeStretchForm


def test():
    p = r"C:\Users\jjaw-\Downloads\harold.jpg"
    # p = r"C:\Users\jjaw-\Downloads\lena.png"

    app = QApplication(sys.argv)
    from image import Image
    img = Image.from_file(p, True)
    img.posterize(2)
    img = img.bitwise_not()
    import numpy as np
    from image import Padding
    img.skeletonize(np.ones((3, 3)), Padding.REFLECT)
    img.show()
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
