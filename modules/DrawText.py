import skia
import utils


class DrawText:
    def __init__(self, x1, y1, text, font, color):
        self.text = text
        self.font = font
        self.color = color
        self.rect = skia.Rect.MakeLTRB(
            x1,
            y1,
            x1 + font.measureText(text),
            y1 + utils.linespace(font),
        )

    def execute(self, canvas):
        paint = skia.Paint(AntiAlias=True, Color=utils.parse_color(self.color))
        baseline = self.rect.top() - self.font.getMetrics().fAscent
        canvas.drawString(
            self.text, float(self.rect.left()), baseline, self.font, paint
        )
