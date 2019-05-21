import requests._internal_utils

def clean_label(label):
    return label.replace("$","D").replace("_","U").replace(".","A")

class SAPLine:
    def __init__(self, type, name, *args):
        self.type = type
        self.name = name
        self.args = args

    def to_string(self):
        indent = "    "
        if self.type == "instruction":
            return indent+self.name+" "+" ".join(self.args)
        elif self.type == "directive":
            return indent+"."+self.name+" "+" ".join(self.args)
        elif self.type == "label":
            return clean_label(self.name)+":"
        elif self.type == "comment":
            return indent+"; "+self.name
        elif self.type == "raw":
            return indent+self.name


class SAPSegment:
    def __init__(self):
        self.lines = []

    def write_inst(self, name, *args):
        self.lines.append(SAPLine("instruction", name, *args))

    def write_directive(self, name, *args):
        self.lines.append(SAPLine("directive", name, *args))

    def write_label(self, name):
        self.lines.append(SAPLine("label", name))

    def write_comment(self, seg):
        self.lines.append(SAPLine("comment", seg))

    def write_spacer(self):
        self.write_raw("")

    def write_line(self, seg):
        self.lines.append(SAPLine("raw", seg))

    def write_seg(self, seg):
        self.lines += seg.lines
    
    def write_lines(self, lines):
        self.lines += [SAPLine("raw", line) for line in lines]
    
    def get_last(self):
        return self.lines[-1]
    
    def get_first(self):
        return self.lines[0]