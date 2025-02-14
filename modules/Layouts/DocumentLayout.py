import config
import utils
from .BlockLayout import BlockLayout


class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []
        self.width = None
        self.x = None
        self.y = None
        self.height = None

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = config.WIDTH - 2 * config.HSTEP
        self.x = config.HSTEP
        self.y = config.HSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []

    def paint_effects(self, cmds):
        cmds = utils.paint_visual_effects(self.node, cmds)
        return cmds

    def should_paint(self):
        return True
