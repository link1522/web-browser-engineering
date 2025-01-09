from .BlockLayout import BlockLayout


WIDTH, HEIGHT = 800, 600


class DocumentLayout:
    HSTEP, VSTEP = 13, 18

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
        self.width = WIDTH - 2 * DocumentLayout.HSTEP
        self.x = DocumentLayout.HSTEP
        self.y = DocumentLayout.HSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []
