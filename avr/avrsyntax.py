import re
from ..preprocessing.util import rcut, lcut, parse_dsv

def split_spaces(text):
    return parse_dsv(text, [" "])[::2]

def detect_linetype(line):
    line = line.strip()

    if re.match("\w+ ?="): # Something like "__SP_H__ = 0x3e"
        return "reg-assign"
    elif re.match("\.\w+"): # Something like ".global main"
        return "directive"
    elif re.match(":$"): # Something like "main:"
        return "label"
    elif re.match("\/\*.+\*\/"): # Something like "/* frame size = 0 */"
        return "comment"
    elif line == "": # Blank line
        return "null"
    else:
        return "instruction"

def parse_avr(asm):
    lines = []

    for line in asm.split("\n"):
        ltype = detect_linetype(line)
        line = None
        if ltype == "directive":
            line = Directive(line)
        elif ltype == "label":
            line = Label(line)
        elif ltype == "comment":
            line = Comment(line)
        elif ltype == "instruction":
            line = Instruction(line)

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
        self.text = lcut(rcut(line, "/*"), "/*")

class Instruction:
    def __init__(self, line):
        self.raw = line
        parts = split_spaces(line)
        self.mne = parts[0]
        self.args = parts[1:]

