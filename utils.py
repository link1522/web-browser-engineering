import tkinter.font

FONTS = {}


def get_font(size, weight, style):
    if weight.isdigit():
        weight = int(weight)
        if weight > 400:
            weight = "bold"
        else:
            weight = "normal"
    key = (size, weight, style)

    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
