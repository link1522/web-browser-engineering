class CSSParser:
    def __init__(self, s):
        self.s = s
        self.i = 0

    def body(self):
        pairs = {}
        while self.i < len(self.s):
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception:
                why = self.ignore_until([";"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        
        return pairs

    def pair(self):
        props = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        val = self.word()
        return props.casefold(), val

    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1
        
    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break
        if not (self.i > start):
            raise Exception("Parsing error")
        return self.s[start:self.i]
    
    def literal(self, literal):
        if not (self.i < len(self.s)) and self.s[self.i] == literal:
            raise Exception("Parsing error")
        self.i += 1
    
    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1
        return None
