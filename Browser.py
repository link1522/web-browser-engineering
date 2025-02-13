import sdl2
import skia
import config
import utils
import sys
from modules.Tab import Tab
from modules.URL import URL
from modules.Chrome import Chrome


class Browser:
    def __init__(self):
        if sdl2.SDL_BYTEORDER == sdl2.SDL_BIG_ENDIAN:
            self.RED_MASK = 0xFF000000
            self.GREEN_MASK = 0x00FF0000
            self.BLUE_MASK = 0x0000FF00
            self.ALPHA_MASK = 0x000000FF
        else:
            self.RED_MASK = 0x000000FF
            self.GREEN_MASK = 0x0000FF00
            self.BLUE_MASK = 0x00FF0000
            self.ALPHA_MASK = 0xFF000000

        self.sdl_window = sdl2.SDL_CreateWindow(
            b"Browser",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            config.WIDTH,
            config.HEIGHT,
            sdl2.SDL_WINDOW_SHOWN,
        )

        self.root_surface = skia.Surface.MakeRaster(
            skia.ImageInfo.Make(
                config.WIDTH,
                config.HEIGHT,
                ct=skia.kRGBA_8888_ColorType,
                at=skia.kUnpremul_AlphaType,
            )
        )
        self.height = config.HEIGHT
        self.width = config.WIDTH
        self.tabs = []
        self.active_tab = None
        self.chrome = Chrome(self)

    def handle_down(self):
        self.active_tab.handle_down()
        self.draw()

    def handle_up(self):
        self.active_tab.handle_up()
        self.draw()

    def handle_mouse_scroll(self, event):
        self.active_tab.handle_mouse_scroll(event)
        self.draw()

    def handle_resize(self, event):
        self.active_tab.handle_resize(event)
        self.draw()

    def handle_click(self, event):
        if event.y < self.chrome.bottom:
            self.focus = None
            self.chrome.click(event.x, event.y)
        else:
            self.focus = "content"
            self.chrome.blur()
            tab_y = event.y - self.chrome.bottom
            self.active_tab.handle_click(event.x, tab_y)
        self.draw()

    def handle_key(self, event):
        if len(event.char) == 0:
            return
        if not (0x20 <= ord(event.char) <= 0x7F):
            return
        if self.chrome.keypress(event.char):
            self.draw()
        elif self.focus == "content":
            self.active_tab.keypress(event.char)
            self.draw()

    def handle_enter(self, event):
        self.chrome.enter()
        self.draw()

    def handle_quit(self):
        sdl2.SDL_DestroyWindow(self.sdl_window)

    def draw(self):
        skia_image = self.root_surface.makeImageSnapshot()
        skia_bytes = skia_image.tobytes()

        depth = 32
        pitch = 4 * config.WIDTH
        sdl_surface = sdl2.SDL_CreateRGBSurfaceFrom(
            skia_bytes,
            config.WIDTH,
            config.HEIGHT,
            depth,
            pitch,
            self.RED_MASK,
            self.GREEN_MASK,
            self.BLUE_MASK,
            self.ALPHA_MASK,
        )
        rect = sdl2.SDL_Rect(0, 0, config.WIDTH, config.HEIGHT)
        window_surface = sdl2.SDL_GetWindowSurface(self.sdl_window)
        sdl2.SDL_BlitSurface(sdl_surface, rect, window_surface, rect)
        sdl2.SDL_UpdateWindowSurface(self.sdl_window)

        self.canvas = self.root_surface.getCanvas()

        self.active_tab.draw(self.canvas, self.chrome.bottom)
        for cmd in self.chrome.paint():
            cmd.execute(0, self.canvas)

    def new_tab(self, url):
        new_tab = Tab(config.HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()


if __name__ == "__main__":
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS)
    browser = Browser()
    browser.new_tab(URL(sys.argv[1]))
    utils.mainloop(browser)
