from .URL import URL
from .Layouts.DocumentLayout import DocumentLayout
from .HTMLParser import HTMLParser
from .Element import Element
from .CSSParser import CSSParser
from .Text import Text

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
DEFAULT_STYLE_SHEET = CSSParser(open("Browser.css").read()).parse()
INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}


class Tab:
    def __init__(self):
        self.height = HEIGHT
        self.width = WIDTH
        self.scroll = 0
        self.url = None

    def handle_click(self, x, y):
        y += self.scroll

        objs = [
            obj
            for obj in tree_to_list(self.document, [])
            if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height
        ]
        if not objs:
            return

        elt = objs[-1].node
        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                url = self.url.resolve(elt.attributes["href"])
                return self.load(url)
            elt = elt.parent

    def handle_down(self):
        max_y = max(self.document.height + 2 * DocumentLayout.VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    def handle_up(self):
        self.scroll -= SCROLL_STEP
        self.scroll = max(self.scroll, 0)

    def handle_mouse_scroll(self, event):
        max_y = max(self.document.height + 2 * DocumentLayout.VSTEP - HEIGHT, 0)

        self.scroll -= event.delta
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

    def load(self, url: URL):
        self.url = url
        body = url.request()
        self.nodes = HTMLParser(body).parse()
        links = [
            node.attributes["href"]
            for node in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]
        rules = DEFAULT_STYLE_SHEET.copy()
        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            rules.extend(CSSParser(body).parse())
        style(self.nodes, sorted(rules, key=cascade_priority))
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)

    def draw(self, canvas):
        canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT or cmd.bottom < self.scroll:
                continue
            cmd.execute(self.scroll, canvas)


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        if isinstance(child.node, Element) and child.node.tag == "head":
            continue
        paint_tree(child, display_list)


def style(node, rules):
    node.style = {}

    for property, default_value in INHERITED_PROPERTIES.items():
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
            parent_font_size = INHERITED_PROPERTIES["font-size"]
        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = f"{parent_px * node_pct}px"

    for child in node.children:
        style(child, rules)


def tree_to_list(tree, list):
    list.append(tree)
    for child in tree.children:
        tree_to_list(child, list)
    return list


def cascade_priority(rule):
    selectors, body = rule
    return selectors.priority
