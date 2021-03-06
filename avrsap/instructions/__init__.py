from ..sap import SAPSegment
from ..addressing import token_to_ptr, token_to_value
from . import arithmetic
from . import data
from . import controlflow

instruction_set = (
    arithmetic.adc,
    arithmetic.add,
    data.ldi,
    data.lds,
    data.sts,
    controlflow.rcall,
    controlflow.ret
)

class InstructionRegistry:
    registry = {}
    
    @staticmethod
    def add(inst):
        InstructionRegistry.registry[inst.__name__] = inst()

    @staticmethod
    def contains(mne):
        return mne in InstructionRegistry.registry
    
    @staticmethod
    def get(mne):
        return InstructionRegistry.registry[mne]

for inst in instruction_set:
    InstructionRegistry.add(inst)

def translate_instruction(mne, args):
    seg = SAPSegment()

    seg.write_comment(mne+" "+" ".join([token.text for token in args]))
    
    if InstructionRegistry.contains(mne):
        inst = InstructionRegistry.get(mne)
        seg.write_seg(inst.run(args, setflags=False))
    else:
        seg = SAPSegment()
        seg.write_comment("[CSAP] Unsupported instruction "+mne)
    
    return seg