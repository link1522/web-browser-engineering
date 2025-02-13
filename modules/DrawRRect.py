import skia
import utils


class DrawRRect:
    def __init__(self, rect, radius, color):
        self.rect = rect
        self.rrect = skia.RRect.MakeRectXY(rect, radius, radius)
        self.color = color

    def execute(self, scroll, canvas):
        paint = skia.Paint(Color=utils.parse_color(self.color))
        canvas.drawRRect(self.rrect.makeOffset(0, -scroll), paint)
