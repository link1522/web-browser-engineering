import urllib
import urllib.parse
import config
import utils
from .URL import URL
from .Layouts.DocumentLayout import DocumentLayout
from .HTMLParser import HTMLParser
from .Element import Element
from .CSSParser import CSSParser
from .Text import Text
from .JSContext import JSContext
from .TaskRunner import TaskRunner
from .Task import Task

DEFAULT_STYLE_SHEET = CSSParser(open("Browser.css").read()).parse()


class Tab:
    def __init__(self, tab_height):
        self.height = config.HEIGHT
        self.width = config.WIDTH
        self.scroll = 0
        self.url = None
        self.tab_height = tab_height
        self.history = []
        self.focus = None
        self.task_runner = TaskRunner(self)
        self.js = None

    def handle_click(self, x, y):
        self.focus = None
        y += self.scroll

        objs = [
            obj
            for obj in utils.tree_to_list(self.document, [])
            if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height
        ]
        if not objs:
            return

        elt = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                if self.js.dispatch_event("click", elt):
                    return
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elif elt.tag == "input":
                if self.js.dispatch_event("click", elt):
                    return
                elt.attributes["value"] = ""
                if self.focus:
                    self.focus.is_focus = False
                self.focus = elt
                elt.is_focus = True
                return self.render()
            elif elt.tag == "button":
                if self.js.dispatch_event("click", elt):
                    return
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent

    def handle_down(self):
        max_y = max(self.document.height + 2 * config.VSTEP - self.tab_height, 0)
        self.scroll = min(self.scroll + config.SCROLL_STEP, max_y)

    def handle_up(self):
        self.scroll -= config.SCROLL_STEP
        self.scroll = max(self.scroll, 0)

    def handle_mouse_scroll(self, event):
        max_y = max(self.document.height + 2 * config.VSTEP - self.tab_height, 0)

        STEP = 15
        self.scroll -= event.y * STEP
        if self.scroll < 0:
            self.scroll = 0
        if self.scroll > max_y:
            self.scroll = max_y

    def handle_resize(self, event):
        self.width = event.width
        self.height = event.height
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        paint_tree(self.document, self.display_list)

    def keypress(self, char):
        if self.focus:
            if self.js.dispatch_event("keydown", self.focus):
                return
            self.focus.attributes["value"] += char
            self.render()

    def submit_form(self, elt):
        if self.js.dispatch_event("submit", self.focus):
            return
        inputs = [
            node
            for node in utils.tree_to_list(elt, [])
            if isinstance(node, Element)
            and node.tag == "input"
            and "name" in node.attributes
        ]

        body = ""
        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes["value"] if "value" in input.attributes else ""
            name = urllib.parse.quote(name)
            value = urllib.parse.quote(value)
            body += "&" + name + "=" + value
        body = body[1:]
        url = self.url.resolve(elt.attributes["action"])
        self.load(url, body)

    def load(self, url: URL, payload=None):
        headers, body = url.request(self.url, payload)
        self.url = url
        self.history.append(self.url)
        self.nodes = HTMLParser(body).parse()

        self.allow_origins = None
        if "content-security-policy" in headers:
            csp = headers["content-security-policy"].split()
            if len(csp) > 0 and csp[0] == "default-src":
                self.allow_origins = []
                for origin in csp[1:]:
                    self.allow_origins.append(URL(origin).origin())

        links = [
            node.attributes["href"]
            for node in utils.tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]
        self.rules = DEFAULT_STYLE_SHEET.copy()
        for link in links:
            style_url = url.resolve(link)
            if not self.allow_request(style_url):
                print("Blocked style sheet", link, "due to CSP")
                continue
            try:
                _, body = style_url.request(url)
            except:
                continue
            self.rules.extend(CSSParser(body).parse())

        scripts = [
            node.attributes["src"]
            for node in utils.tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "script"
            and "src" in node.attributes
        ]
        if self.js:
            self.js.discarded = True
        self.js = JSContext(self)
        for script in scripts:
            script_url = url.resolve(script)
            if not self.allow_request(script_url):
                print("Blocked script", script, "due to CSP")
                continue
            try:
                _, body = script_url.request(url)
            except:
                continue
            task = Task(self.js.run, script_url, body)
            self.task_runner.schedule_task(task)

        self.render()

    def allow_request(self, url):
        return self.allow_origins == None or url.origin() in self.allow_origins

    def render(self):
        style(self.nodes, sorted(self.rules, key=cascade_priority))
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)

    def raster(self, canvas):
        for cmd in self.display_list:
            cmd.execute(canvas)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)


def paint_tree(layout_object, display_list):
    if layout_object.should_paint():
        cmds = layout_object.paint()
    for child in layout_object.children:
        paint_tree(child, cmds)

    # If the page fails to render properly, comment out the following lines to disable opacity effects.
    if layout_object.should_paint():
        cmds = layout_object.paint_effects(cmds)

    display_list.extend(cmds)


def style(node, rules):
    node.style = {}

    for property, default_value in config.INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    for selector, body in rules:
        if not selector.matches(node):
            continue
        for property, value in body.items():
            node.style[property] = value

    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value

    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = config.INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = f"{parent_px * node_pct}px"

    for child in node.children:
        style(child, rules)


def cascade_priority(rule):
    selectors, body = rule
    return selectors.priority
