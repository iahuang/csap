import re
from .avr import parse_avr, Directive, Comment, Instruction, Label
from .sap import SAPSegment

from .directives import translate_directive
from .instructions import translate_instruction


class Translator:
    def __init__(self, header, stack_size=100):
        self.avrinit = SAPSegment()
        self.avrheader = header
        self.main = SAPSegment()
        self.stack_size = stack_size

    def process(self, text):
        syntax = parse_avr(text)

        avrinit = SAPSegment()

        avrinit.write_label("avrinit")

        # Initialize stack pointer
        avrinit.write_inst("movar", "programEnd", "r1")
        avrinit.write_inst("movrm", "r1", "stackptr")

        # Code for the initial call to main
        avrinit.write_lines([
            "push r2",
            "movar initCheckpoint r2",
            "addir #2 r2",
            "call avrpush r2",
            "pop r2",
            "initCheckpoint: jmp main"
        ])

        main = SAPSegment()

        for line in syntax:
            if isinstance(line, Directive):
                seg, headseg = translate_directive(line)
                main.write_seg(seg)
                avrinit.write_seg(headseg)
            elif isinstance(line, Comment):
                main.write_comment("[GCC] "+line.text)
            elif isinstance(line, Label):
                main.write_label(line.name)
            elif isinstance(line, Instruction):
                mne = line.name
                args = line.args
                main.write_seg(translate_instruction(mne, args))
        
        avrinit.write_inst("halt")
        self.avrinit = avrinit

        main.write_label("programEnd")
        main.write_directive("integer", "#0")
        self.main = main

    def build_segment(self, seg):
        output = ""

        for line in seg.lines:
            output += line.to_string()+"\n"
        return output

    def to_sap(self, text):
        self.process(text)
        output = ""

        output += self.build_segment(self.avrinit)
        output += self.build_segment(self.main)

        return self.avrheader+output
