import sdl2
import ctypes
import skia
import math
import sys
import config
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
        self.tabs = []
        self.active_tab = None
        self.chrome = Chrome(self)

        self.chrome_surface = skia.Surface(config.WIDTH, math.ceil(self.chrome.bottom))
        self.tab_surface = None

    def handle_down(self):
        self.active_tab.handle_down()
        self.raster_tab()
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
            self.raster_chrome()
        else:
            self.focus = "content"
            self.chrome.blur()
            url = self.active_tab.url
            tab_y = event.y - self.chrome.bottom
            self.active_tab.handle_click(event.x, tab_y)

            if self.active_tab.url != url:
                self.raster_chrome()
            self.raster_tab()
        self.draw()

    def handle_key(self, char):
        if len(char) == 0:
            return
        if not (0x20 <= ord(char) <= 0x7F):
            return
        if self.chrome.keypress(char):
            self.raster_chrome()
            self.draw()
        elif self.focus == "content":
            self.active_tab.keypress(char)
            self.raster_tab()
            self.draw()

    def handle_enter(self):
        self.chrome.enter()
        self.raster_chrome()
        self.raster_tab()
        self.draw()

    def handle_quit(self):
        sdl2.SDL_DestroyWindow(self.sdl_window)

    def draw(self):

        canvas = self.root_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)

        tab_rect = skia.Rect.MakeLTRB(
            0, self.chrome.bottom, config.WIDTH, config.HEIGHT
        )
        tab_offset = self.chrome.bottom - self.active_tab.scroll
        canvas.save()
        canvas.clipRect(tab_rect)
        canvas.translate(0, tab_offset)
        self.tab_surface.draw(canvas, 0, 0)
        canvas.restore()

        chrome_rect = skia.Rect.MakeLTRB(0, 0, config.WIDTH, self.chrome.bottom)
        canvas.save()
        canvas.clipRect(chrome_rect)
        self.chrome_surface.draw(canvas, 0, 0)
        canvas.restore()

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

    def raster_tab(self):
        tab_height = math.ceil(self.active_tab.document.height + 2 * config.VSTEP)

        if not self.tab_surface or tab_height != self.tab_surface.height():
            self.tab_surface = skia.Surface(config.WIDTH, tab_height)

        canvas = self.tab_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        self.active_tab.raster(canvas)

    def raster_chrome(self):
        canvas = self.chrome_surface.getCanvas()
        canvas.clear(skia.ColorWHITE)
        for cmd in self.chrome.paint():
            cmd.execute(canvas)

    def new_tab(self, url):
        new_tab = Tab(config.HEIGHT - self.chrome.bottom)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.raster_tab()
        self.raster_chrome()
        self.draw()


def mainloop(browser):
    event = sdl2.SDL_Event()
    while True:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                browser.handle_quit()
                sdl2.SDL_Quit()
                sys.exit()
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                browser.handle_click(event.button)
            elif event.type == sdl2.SDL_MOUSEWHEEL:
                browser.handle_mouse_scroll(event.wheel)
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RETURN:
                    browser.handle_enter()
                elif event.key.keysym.sym == sdl2.SDLK_DOWN:
                    browser.handle_down()
                elif event.key.keysym.sym == sdl2.SDLK_UP:
                    browser.handle_up()
            elif event.type == sdl2.SDL_TEXTINPUT:
                browser.handle_key(event.text.text.decode("utf8"))

        browser.active_tab.task_runner.run()



if __name__ == "__main__":
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS)
    browser = Browser()
    browser.new_tab(URL(sys.argv[1]))
    mainloop(browser)
