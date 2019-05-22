from ..sap import SAPSegment
from ..addressing import token_to_ptr, token_to_value
from .tools import load_args

def lds(args):
    seg = SAPSegment()
    load_args(seg, args)

    seg.write_inst("movrx","r2","r1")

    return seg
    

