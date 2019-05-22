from .sap import SAPSegment
from .addressing import token_to_ptr, token_to_value

def translate_instruction(mne, args):
    seg = SAPSegment()
    seg.write_comment(mne+" "+" ".join([token.text for token in args]))

    if mne == "lds":
        seg.write_seg(lds(args))
    else:
        seg = SAPSegment()
        seg.write_comment("[CSAP] Unsupported instruction "+mne)
    return seg

def lds(args):
    seg = SAPSegment()

    seg.write_seg(token_to_ptr(args[0], 1))
    seg.write_seg(token_to_value(args[1], 2))

    seg.write_inst("movrx","r2","r1")

    return seg