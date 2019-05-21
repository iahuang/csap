import re
from .util import rcut, lcut, parse_dsv

def split_spaces(text):
    return parse_dsv(text, [" "])[::2]

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
    

class Directive:
    def __init__(self, line):
        self.raw = line
        parts = split_spaces(line)
        self.name = parts[0].lstrip(".")
        self.args = parts[1:]

class Label:
    def __init__(self, line):
        self.raw = line
        self.name = line.rstrip(":")

class Comment:
    def __init__(self, line):
        self.raw = line
        self.text = rcut(lcut(line, "/*"), "*/")

class Instruction:
    def __init__(self, line):
        self.raw = line
        parts = split_spaces(line)
        self.mne = parts[0]
        self.args = list([Token(arg) for arg in parts[1:] ])

class Token:
    def __init__(self, text):
        if re.match("r\d+", text):
            self.type = "register"
        elif re.match("\d+", text):
            self.type = "constant"
        else:
            self.type = "computed"


