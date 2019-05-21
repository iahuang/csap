import re
import os
from assembly.util import resource_path, lcut, rcut
from assembly.x86 import Parser, Token, parse_token

REG32 = ["eax", "ebx", "ecx", "edx", "edi", "esi", "esp", "ebp"]
REG16 = ["ax", "bx", "cx", "dx"]
HI8 = ["ah", "bh", "ch", "dh"]
LO8 = ["al", "bl", "cl", "dl"]
REGS = REG32+REG16+HI8+LO8

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


class SAPProgramSegment:
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

    def write_raw(self, seg):
        self.lines.append(SAPLine("raw", seg))

    def write_seg(self, seg):
        self.lines += seg.lines
    
    def write_raw_lines(self, lines):
        self.lines += [SAPLine("raw", line) for line in lines]
    
    def get_last(self):
        return self.lines[-1]
    
    def get_first(self):
        return self.lines[0]


class x86toSAP:
    def __init__(self, header, stack_size=100):
        self.parser = Parser()

        self.header = header

        self.bss_section = SAPProgramSegment()
        self.init = SAPProgramSegment()
        self.prg = SAPProgramSegment()

        self.init.write_label("x86init")

        self.next_checkpoint_id = 0
        self.stack_size = stack_size

    def convert_directive(self, directive):
        name = directive.name
        args = directive.args

        numeric_directives = ["zero", "value", "long"]
        str_directives = ["asciz", "ascii", "string"]

        if name in numeric_directives:
            if re.fullmatch("\\d+", args[0]):
                self.prg.write_directive("integer", "#"+args[0])
            else:
                last_label = self.prg.get_last()
                if last_label.type != "label":
                    print("Throwing")
                    exit()
                
                self.init.write_inst("movar", clean_label(args[0]), "r1")
                self.init.write_inst("movrm", "r1", last_label.name)
                self.prg.write_directive("integer", "#0")
        elif name in str_directives:
            self.prg.write_directive("string", args[0])
        elif name == "comm":
            name, size, align = args
            self.bss_section.write_label(name)
            self.bss_section.write_directive("allocate", "#"+size)

    def convert_label(self, label):
        self.prg.write_label(label.name)

    def ptr_term(self, token, reg_num):
        seg = SAPProgramSegment()
        reg = "r"+str(reg_num)
        if token.type == "register":
            seg.write_inst("movmr", token.value, reg)
        elif token.type == "constant":
            seg.write_inst("movir", "#"+token.value, reg)
        elif token.type == "label":
            seg.write_inst("movar", token.value, reg)
        return seg

    def computed_ptr(self, token, reg_num):
        seg = SAPProgramSegment()
        reg = "r"+str(reg_num)

        if not token.value.startswith("dword ptr"):
            print("unsupported computation")
            exit()
        
        expr = lcut(token.value, "dword ptr").strip().lstrip('[').rstrip(']').replace(' ', '')
        terms = re.split('\+|-', expr)
        ops = re.findall('[\+-]', expr)
        seg.write_seg(self.ptr_term(parse_token(terms[0]), 3))
        term_reg_num = 4
        for term, op in zip(terms[1:], ops):
            term_reg = "r"+str(term_reg_num)
            seg.write_seg(self.ptr_term(parse_token(term), term_reg_num))
            if op == "+":
                seg.write_inst("addrr", term_reg, reg)
            elif op == "-":
                seg.write_inst("subrr", term_reg, reg)
            term_reg_num+=1
        seg.write_inst("movrr", "r3", reg)

        return seg

    def to_register(self, token, reg_num):
        seg = SAPProgramSegment()
        reg = "r"+str(reg_num)

        if token.type == "register":
            seg.write_inst("movmr", token.value, reg)
        elif token.type == "constant":
            seg.write_inst("movir", "#"+token.value, reg)
        elif token.type == "computed":
            seg.write_seg(self.computed_ptr(token, reg_num))
            seg.write_inst("movxr", reg, reg)
        else:
            seg.write_comment("unknown token type "+token.type)
        return seg
    
    def to_ptr_register(self, token, reg_num):
        seg = SAPProgramSegment()
        reg = "r"+str(reg_num)
        
        if token.type == "register":
            seg.write_inst("movar", token.value, reg)
        elif token.type == "constant":
            print("A constant cannot be assigned to")
        elif token.type == "label":
            seg.write_inst("movar", token.value, reg)
        elif token.type == "computed":
            seg.write_seg(self.computed_ptr(token, reg_num))
        else:
            seg.write_comment("unknown token type "+token.type)

        return seg

    def convert_inst(self, inst):
        seg = SAPProgramSegment()
        mne = inst.inst # mne pohoi
        args = inst.args
        if mne == "push":
            seg.write_seg(self.to_register(args[0], 1))
            seg.write_raw("call x86push r1")
        elif mne == "pop":
            seg.write_seg(self.to_ptr_register(args[0], 1))
            seg.write_raw("call x86pop")
            seg.write_inst("movrx", "r0", "r1")
        elif mne == "and":
            seg.write_seg(self.to_register(args[1], 1)) # Src
            seg.write_seg(self.to_ptr_register(args[0], 2)) # Dest
            seg.write_raw("call tobinary r1 &bin1")
            seg.write_raw("call tobinary r2 &bin2")
            seg.write_raw("call bitwiseand &bin1 &bin2 &bin3")
            seg.write_raw("call todecimal &bin3")
            seg.write_inst("movrx", "r0", "r2")
            seg.write_inst("clrm", "cf")
            seg.write_inst("clrm", "of")
            seg.write_raw_lines([
                "if r0 == #0",
                "   zf = #1",
                "else",
                "   zf = #0",
                "endif"
            ])
            seg.write_raw("sf = *bin3") # set sign flag to the sign bit of the result
            seg.write_raw("cf = #0")
            seg.write_raw("of = #0")
        elif mne == "mov":
            seg.write_seg(self.to_register(args[1], 1))
            seg.write_seg(self.to_ptr_register(args[0], 2))
            seg.write_inst("movrx", "r1", "r2")
        elif mne == "lea":
            seg.write_seg(self.to_ptr_register(args[1], 1)) # Source
            seg.write_seg(self.to_ptr_register(args[0], 2)) # Dest
            seg.write_inst("movrx", "r1", "r2")
        elif mne == "call":
            return_label = "checkpoint"+str(self.next_checkpoint_id)
            seg.write_inst("push", "r2")
            seg.write_inst("movar", return_label, "r2")
            seg.write_inst("addir", "#2", "r2") # Create a custom return location based on the location of the jsr instruction
            seg.write_raw("call x86push r2") # Push the return location onto the stack
            seg.write_inst("pop", "r2")
            seg.write_label(return_label)
            seg.write_inst("jmp", args[0].value)
            self.next_checkpoint_id+=1
        elif mne == "ret":
            seg.write_raw("call x86ret")
        elif mne == "jmp":
            seg.write_inst("jmp", args[0].value)
        elif mne == "jne":
            seg.write_raw_lines([
                "if *zf == #0",
                "   jmp "+args[0].value,
                "endif"
            ])
        elif mne == "je":
            seg.write_raw_lines([
                "if *sf != *of",
                "   jmp "+args[0].value,
                "endif"
            ])
        elif mne == "jle":
            seg.write_raw_lines([
                "if *sf == *of",
                "   jmp "+args[0].value,
                "endif"
            ])
        elif mne == "test":
            seg.write_seg(self.to_register(args[0], 1))
            seg.write_seg(self.to_register(args[1], 2))
            seg.write_raw("call tobinary r1 &bin1")
            seg.write_raw("call tobinary r2 &bin2")
            seg.write_raw("call bitwiseand &bin1 &bin2 &bin3")
            seg.write_raw("call todecimal &bin3")
            seg.write_inst("clrm", "cf")
            seg.write_inst("clrm", "of")
            seg.write_raw_lines([
                "if r0 == #0",
                "   zf = #1",
                "else",
                "   zf = #0",
                "endif"
            ])
            seg.write_raw("sf = *bin3") # set sign flag to the sign bit of the result
            seg.write_raw("cf = #0")
            seg.write_raw("of = #0")
        elif mne == "add":
            seg.write_seg(self.to_register(args[1], 1))
            seg.write_seg(self.to_ptr_register(args[0], 2))
            seg.write_inst("addrx", "r1", "r2")
        elif mne == "sub":
            seg.write_seg(self.to_register(args[1], 1))
            seg.write_seg(self.to_ptr_register(args[0], 2))
            seg.write_inst("subrx", "r1", "r2")
        else:
            seg.write_comment("unknown command "+inst.inst)
        return seg
    def dump_program_segment(self, seg):
        output = ""
        for line in seg.lines:
            output += line.to_string()
            #if line.type != "label":
            output += "\n"
        return output+"\n"

    def finalize(self):
        output = self.header+"\n"
        output += self.dump_program_segment(self.bss_section)
        output += self.dump_program_segment(self.init)
        output += self.dump_program_segment(self.prg)

        return output

    def convert(self, string):
        self.parser.parse(string)
        for line in self.parser.lines:
            if line.type == "directive":
                self.convert_directive(line)
            elif line.type == "label":
                self.convert_label(line)
            elif line.type == "instruction":
                seg = self.convert_inst(line)
                self.prg.write_seg(seg)
                self.prg.write_spacer()
        
        self.init.write_inst("movar", "programend", "r1")
        self.init.write_inst("addir", "#"+str(self.stack_size), "r1")
        self.init.write_inst("movrm", "r1", "esp")

        self.init.write_inst("movar", "end", "r2")
        self.init.write_inst("addir", "#2", "r2")
        self.init.write_raw("call x86push r2") # Pretend to push the program counter on the stack
        self.init.write_label("end")
        self.init.write_inst("jmp", "Umain") 
        self.init.write_inst("halt")

        self.prg.write_label("programend")
        self.prg.write_inst("nop")
    
        return self.finalize()
