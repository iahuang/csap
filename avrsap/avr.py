import re
from .util import rcut, lcut, parse_dsv

class meta: # Defines important constants for AVR
    wordbits = 16
    wordsize = 2
    intbits = 32
    intsize = 4
    longbits = 32
    longsize = 4
    longlongbits = 64
    longlongsize = 8

def split_spaces(text):
    return parse_dsv(text, [" "])[::2]

def grouped_replace(text, query, to):
    parts = parse_dsv(text, [query])

    for i, part in enumerate(parts):
        if part == query:
            parts[i] = to

    return "".join(parts)

def detect_linetype(line):
    line = line.strip()

    if re.match("\w+ ?=", line): # Something like "__SP_H__ = 0x3e"
        return "reg-assign"
    elif re.match("\.\w+", line): # Something like ".global main"
        return "directive"
    elif re.search(":$", line): # Something like "main:"
        return "label"
    elif re.match("\/\*.+\*\/", line): # Something like "/* frame size = 0 */"
        return "comment"
    elif line == "": # Blank line
        return "null"
    else:
        return "instruction"

def parse_avr(asm):
    lines = []

    for linetext in asm.split("\n"):
        linetext = linetext.strip()
        linetext = grouped_replace(linetext, "\t", " ")
        
        ltype = detect_linetype(linetext)
        line = None
        if ltype == "directive":
            line = Directive(linetext)
        elif ltype == "label":
            line = Label(linetext)
        elif ltype == "comment":
            line = Comment(linetext)
        elif ltype == "instruction":
            line = Instruction(linetext)
        
        if line:
            lines.append(line)
    
    return lines


class Label:
    def __init__(self, line):
        self.raw = line
        self.name = line.rstrip(":")

class Comment:
    def __init__(self, line):
        self.raw = line
        self.text = rcut(lcut(line, "/*"), "*/")

class Argumented:
    def __init__(self, line):
        self.name = line.split(" ")[0]
        self.args = parse_dsv(lcut(line, self.name+" "), [","])[::2]
        self.args = list([arg.strip() for arg in self.args])

class Directive(Argumented):
    def __init__(self, line):
        self.raw = line
        super().__init__(line.lstrip("."))

class Instruction(Argumented):
    def __init__(self, line):
        self.raw = line
        super().__init__(line)
        self.args = list([Token(arg) for arg in self.args])

class Token:
    def __init__(self, text):
        if re.match("r\d+", text):
            self.type = "register"
        elif re.match("\d+", text):
            self.type = "constant"
        else:
            self.type = "computed"


