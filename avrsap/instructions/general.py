from ..sap import SAPSegment

from ..addressing import token_to_ptr, token_to_value

class StatusFlags:
    CARRY = 0b1
    ZERO = 0b10
    NEG = 0b100

    _flagsize = 3
    all = 2**_flagsize
    none = 0
    numeric = CARRY | ZERO | NEG

class Instruction:
    def __init__(self, flags=StatusFlags.none):
        self.flags = flags
        self.shouldsetflags = False

    def run(self, args, setflags):
        self.shouldsetflags = setflags
        self.args = args
        self.seg = SAPSegment()
        self.on_run()
        return self.seg

    def on_run(self):
        print("Warning: Can't run transpile generic Instruction")
        return seg
    
    def setflags(self, value_register, force=False):
        if not self.shouldsetflags and not force:
            return

        if self.flags & StatusFlags.CARRY:
            set_carry(self.seg, value_register)

        if self.flags & StatusFlags.NEG:
            set_neg(self.seg, value_register)
        
        if self.flags & StatusFlags.ZERO:
            set_zero(self.seg, value_register)
    
    def load_args(self, t1="ptr", t2="value"):
        funcs = {"ptr":token_to_ptr,"value":token_to_value}

        self.seg.write_seg(funcs[t1](self.args[0], 1))
        self.seg.write_seg(funcs[t2](self.args[1], 2))

def set_zero(seg, reg):
    seg.write_lines([
        f"if {reg} == #0",
        "movim #1 zero",
        "else",
        "movim #0 zero",
        "endif"
    ])

def set_neg(seg, reg):
    seg.write_lines([
        f"if {reg} > #127",
        "movim #1 negative",
        "else",
        f"if {reg} < #0",
        f"mulir #-1 {reg}",
        f"addir #128 {reg}",
        "movim #1 negative",
        "else",
        "movim #0 negative",
        "endif",
        "endif"
    ])

def set_carry(seg, reg):
    seg.write_lines([
        f"if {reg} > #255",
        f"movir #255 {reg}",
        "movim #1 carry",
        "else",
        "movim #0 carry",
        "endif"
    ])