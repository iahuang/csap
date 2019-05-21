from .sap import SAPSegment
import struct

def intvalue(size, value):
    seg = SAPSegment()
    endian = "<"
    if size == 2:
        t = "h"
    elif size == 4:
        t = "i"
    elif size == 8:
        t = "l"
    
    if value < 0:
        t = t.upper()
    
    b = struct.pack(endian+t, value)
    for byte in b:
        seg.write_directive("integer", "#"+str(byte))

    return seg

def translate_directive(directive):
    header = SAPSegment()

    name = directive.name

    if name == "comm":
        lbl = directive.args[0]
        size = directive.args[1]

        header.write_directive("allocate", "#"+size)
    
    return SAPSegment()
