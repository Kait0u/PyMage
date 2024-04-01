from image import Image
from image_window import ImageWindow


def add_image(callee: ImageWindow | None = None):
    from forms.image_arithmetic_form import ImageArithmeticForm

    result = ImageArithmeticForm.show_dialog("+", callee)
    if result is None: return
    im1, im2, name = result
    new_image = Image.add_images(im1, im2, name)
    new_window = ImageWindow(new_image)
    new_window.show()


def subtract_image(callee: ImageWindow | None = None):
    from forms.image_arithmetic_form import ImageArithmeticForm

    result = ImageArithmeticForm.show_dialog("-", callee)
    if result is None: return
    im1, im2, name = result
    new_image = Image.subtract_images(im1, im2, name)
    new_window = ImageWindow(new_image)
    new_window.show()


def bitwise_and_image(callee: ImageWindow | None = None):
    from forms.image_arithmetic_form import ImageArithmeticForm

    result = ImageArithmeticForm.show_dialog("AND", callee)
    if result is None: return
    im1, im2, name = result
    new_image = Image.bitwise_and_images(im1, im2, name)
    new_window = ImageWindow(new_image)
    new_window.show()


def bitwise_or_image(callee: ImageWindow | None = None):
    from forms.image_arithmetic_form import ImageArithmeticForm

    result = ImageArithmeticForm.show_dialog("OR", callee)
    if result is None: return
    im1, im2, name = result
    new_image = Image.bitwise_or_images(im1, im2, name)
    new_window = ImageWindow(new_image)
    new_window.show()


def bitwise_xor_image(callee: ImageWindow | None = None):
    from forms.image_arithmetic_form import ImageArithmeticForm

    result = ImageArithmeticForm.show_dialog("XOR", callee)
    if result is None: return
    im1, im2, name = result
    new_image = Image.bitwise_xor_images(im1, im2, name)
    new_window = ImageWindow(new_image)
    new_window.show()


def bitwise_not_image(callee: ImageWindow | None = None):
    from forms.bitwise_not_form import BitwiseNotForm

    result = BitwiseNotForm.show_dialog(callee)
    if result is None: return
    im, name = result
    new_image = Image.bitwise_not_image(im, name)
    new_window = ImageWindow(new_image)
    new_window.show()


def blend_image(callee: ImageWindow | None = None):
    from forms.blend_form import BlendForm

    result = BlendForm.show_dialog(callee)
    if result is None: return
    im1, im2, alpha, beta, gamma, name = result
    new_image = Image.blend_images(im1, alpha, im2, beta, gamma, name)
    new_window = ImageWindow(new_image)
    new_window.show()