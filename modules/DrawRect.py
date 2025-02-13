import skia
import utils


class DrawRect:
    def __init__(self, rect, color):
        self.rect = rect
        self.color = color

    def execute(self, canvas):
        paint = skia.Paint(Color=utils.parse_color(self.color))
        canvas.drawRect(self.rect, paint)
