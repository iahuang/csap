from .general import Instruction, StatusFlags

class rcall(Instruction):
    def __init__(self):
        self.next_checkpoint_id = 0
        super().__init__()
    def on_run(self):
        return_label = "checkpoint"+str(self.next_checkpoint_id)
        self.seg.write_inst("push", "r2")
        self.seg.write_inst("movar", return_label, "r2")
        self.seg.write_inst("addir", "#2", "r2") # Create a custom return location based on the location of the jsr instruction
        self.seg.write_line("call avrpush r2") # Push the return location onto the stack
        self.seg.write_inst("pop", "r2")
        self.seg.write_label(return_label)
        self.seg.write_inst("jmp", self.args[0].value)

class ret(Instruction):
    def on_run(self):
        self.seg.write_line("call avrret") # Defined in header