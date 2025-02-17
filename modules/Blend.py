import skia
import utils


class Blend:
    def __init__(self, blend_mode, children):
        self.blend_mode = blend_mode
        self.children = children
        self.rect = skia.Rect.MakeEmpty()
        for cmd in self.children:
            self.rect.join(cmd.rect)

    def execute(self, canvas):
        paint = skia.Paint(BlendMode=utils.parse_blend_mode(self.blend_mode))
        canvas.saveLayer(None, paint)
        for cmd in self.children:
            cmd.execute(canvas)
        canvas.restore()
