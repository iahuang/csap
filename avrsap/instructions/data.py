from .general import Instruction, StatusFlags

class lds(Instruction):
    def on_run(self):
        self.load_args()
        self.seg.write_inst("movrx","r2","r1")

class ldi(Instruction):
    def on_run(self):
        self.load_args()
        self.seg.write_inst("movrx","r2","r1")

class sts(Instruction):
    def on_run(self):
        self.load_args()
        self.seg.write_inst("movrx","r2","r1")