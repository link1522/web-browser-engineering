import tkinter
import sys
from URL import URL
from Layout import Layout
from HTMLParser import HTMLParser

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
        self.display_list = Layout(self.nodes).display_list
        self.draw()

    def load(self, url: URL):
        body = url.request()
        self.nodes = HTMLParser(body).parse()
        self.display_list = Layout(self.nodes).display_list
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c, font in self.display_list:
            if y > self.height + self.scroll or y + Layout.VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c, anchor="nw", font=font)


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
