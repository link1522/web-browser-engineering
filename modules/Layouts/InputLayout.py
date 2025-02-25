import skia
import utils
from ..DrawText import DrawText
from ..DrawRect import DrawRect
from ..DrawLine import DrawLine
from ..Text import Text


class InputLayout:
    INPUT_WIDTH_PX = 200

    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        if style == "normal":
            style = "roman"
        size = int(float(self.node.style["font-size"][:-2]) * 0.75)
        self.font = utils.get_font(size, weight, style)
        self.width = InputLayout.INPUT_WIDTH_PX

        if self.previous:
            space = self.previous.font.measureText(" ")
            self.x = self.previous.x + space + self.previous.width
        else:
            self.x = self.parent.x

        self.height = utils.linespace(self.font)

    def self_rect(self):
        return skia.Rect.MakeLTRB(
            self.x, self.y, self.x + self.width, self.y + self.height
        )

    def paint(self):
        cmds = []
        bgcolor = self.node.style.get("background-color", "transparent")

        if bgcolor != "transparent":
            rect = DrawRect(self.self_rect(), bgcolor)
            cmds.append(rect)

        if self.node.tag == "input":
            text = self.node.attributes.get("value", "")
        elif self.node.tag == "button":
            if len(self.node.children) == 1 and isinstance(self.node.children[0], Text):
                text = self.node.children[0].text
        else:
            print("ignoring HTML contents inside button")
            text = ""

        color = self.node.style["color"]
        cmds.append(DrawText(self.x, self.y, text, self.font, color))

        if self.node.is_focus:
            cx = self.x + self.font.measureText(text)
            cmds.append(DrawLine(cx, self.y, cx, self.y + self.height, "black", 1))

        return cmds

    def paint_effects(self, cmds):
        cmds = utils.paint_visual_effects(self.node, cmds, self.self_rect())
        return cmds

    def should_paint(self):
        return True
