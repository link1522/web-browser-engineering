import tkinter
import sys
from URL import URL

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
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
        self.display_list = layout(self.text, self.width)
        self.draw()

    def load(self, url: URL):
        body = url.request()
        self.text = lex(body)
        self.display_list = layout(self.text, self.width)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.height + self.scroll or y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)


def lex(body):
    in_tag = False
    content = ""

    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            content += c

    content = content.replace("&lt;", "<").replace("&gt;", ">")
    return content


def layout(text, width=WIDTH):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= width - HSTEP or c == "\n":
            cursor_y += VSTEP
            cursor_x = HSTEP

    return display_list


if __name__ == "__main__":
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
