import tkinter
import tkinter.font
import sys
from URL import URL
from Layout import Layout
from Text import Text
from Tag import Tag

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.height = HEIGHT
        self.width = WIDTH
        self.window = tkinter.Tk()
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mouseScroll)
        self.window.bind("<Configure>", self.resize)
        self.canvas = tkinter.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack(fill="both", expand=True)
        self.scroll = 0

    def scrolldown(self, event):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, event):
        self.scroll -= SCROLL_STEP
        self.draw()

    def mouseScroll(self, event):
        self.scroll -= event.delta
        if self.scroll < 0:
            self.scroll = 0
        self.draw()

    def resize(self, event):
        self.width = event.width
        self.height = event.height
        self.display_list = Layout(self.tokens).display_list
        self.draw()

    def load(self, url: URL):
        body = url.request()
        self.tokens = lex(body)
        self.display_list = Layout(self.tokens).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c, font in self.display_list:
            if y > self.height + self.scroll or y + Layout.VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c, anchor="nw", font=font)


def lex(body):
    out = []
    buffer = ""
    in_tag = False

    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
                out.append(Text(buffer))
                buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))

    return out


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
