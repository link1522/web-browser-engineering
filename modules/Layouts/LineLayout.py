class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        for word in self.children:
            word.layout()

        max_accent = -min(
            [word.font.getMetrics().fAscent for word in self.children], default=0
        )
        baseline = self.y + 1.25 * max_accent
        for word in self.children:
            word.y = baseline + word.font.getMetrics().fAscent
        max_descent = max(
            [word.font.getMetrics().fDescent for word in self.children], default=0
        )
        self.height = (max_accent + max_descent) * 1.25

    def paint(self):
        return []

    def should_paint(self):
        return False
