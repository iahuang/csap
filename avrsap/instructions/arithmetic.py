from .general import Instruction, StatusFlags

class add(Instruction):
    def __init__(self):
        super().__init__(StatusFlags.numeric)

    def on_run(self):
        self.load_args(t1="ptr", t2="value")
        self.seg.write_inst("movxr", "r1", "r3")

        self.setflags("r3")

        self.seg.write_inst("addrr", "r2", "r3")
        self.seg.write_inst("movrx", "r3", "r1")

class adc(Instruction):
    def __init__(self):
        super().__init__(StatusFlags.numeric)

    def on_run(self):
        self.load_args(t1="ptr", t2="value")
        self.seg.write_inst("movxr", "r1", "r3")

        self.setflags("r3")

        self.seg.write_inst("addrr", "r2", "r3")
        self.seg.write_inst("addmr", "carry", "r3")
        self.seg.write_inst("movrx", "r3", "r1")
        