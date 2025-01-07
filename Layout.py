from Text import Text
import tkinter.font


class Layout:
    HSTEP, VSTEP = 13, 18

    def __init__(self, tokens):
        self.width = 800
        self.display_list = []
        self.cursor_x = Layout.HSTEP
        self.cursor_y = Layout.VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12

        for tok in tokens:
            self.token(tok)

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4

    def word(self, word):
        font = tkinter.font.Font(
            size=self.size,
            weight=self.weight,
            slant=self.style,
        )
        w = font.measure(word)

        if self.cursor_x + w >= self.width - Layout.HSTEP:
            self.cursor_y += font.metrics("linespace") * 1.25
            self.cursor_x = Layout.HSTEP

        self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        self.cursor_x += w + font.measure(" ")
