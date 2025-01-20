import tkinter
import config
from modules.Tab import Tab
from modules.URL import URL


class Browser:
    def __init__(self):
        self.height = config.HEIGHT
        self.width = config.WIDTH
        self.tabs = []
        self.active_tab = None
        self.window = tkinter.Tk()
        self.window.bind("<Down>", self.handle_down)
        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<MouseWheel>", self.handle_mouse_scroll)
        self.window.bind("<Configure>", self.handle_resize)
        self.window.bind("<Button-1>", self.handle_click)
        self.canvas = tkinter.Canvas(
            self.window, width=self.width, height=self.height, bg="white"
        )
        self.canvas.pack(fill="both", expand=True)

    def handle_down(self, event):
        self.active_tab.handle_down()
        self.draw()

    def handle_up(self, event):
        self.active_tab.handle_up()
        self.draw()

    def handle_mouse_scroll(self, event):
        self.active_tab.handle_mouse_scroll(event)
        self.draw()

    def handle_resize(self, event):
        self.active_tab.handle_resize(event)
        self.draw()

    def handle_click(self, event):
        self.active_tab.handle_click(event.x, event.y)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas)

    def new_tab(self, url):
        new_tab = Tab()
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()


if __name__ == "__main__":
    import sys

    Browser().new_tab(URL(sys.argv[1]))
    tkinter.mainloop()
