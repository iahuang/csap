import re
from .avr import parse_avr, Directive, Comment, Instruction, Label
from .sap import SAPSegment

from .directives import translate_directive
from .instructions import translate_instruction


class Translator:
    def __init__(self, header):
        self.header = SAPSegment()
        self.avrheader = header
        self.main = SAPSegment()

    def process(self, text):
        syntax = parse_avr(text)

        header = SAPSegment()
        main = SAPSegment()

        for line in syntax:
            if isinstance(line, Directive):
                seg, headseg = translate_directive(line)
                main.write_seg(seg)
                header.write_seg(headseg)
            elif isinstance(line, Comment):
                main.write_comment("[GCC] "+line.text)
            elif isinstance(line, Label):
                main.write_label(line.name)
            elif isinstance(line, Instruction):
                mne = line.name
                args = line.args
                main.write_seg(translate_instruction(mne, args))
                
        self.header = header
        self.main = main

    def build_segment(self, seg):
        output = ""

        for line in seg.lines:
            output += line.to_string()+"\n"
        return output

    def to_sap(self, text):
        self.process(text)
        output = ""

        output += self.build_segment(self.header)
        output += self.build_segment(self.main)

        return self.avrheader+output
