from .sap import SAPSegment
from .avr import meta
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

def translate_directive(directive, comment_unused=False):
    header = SAPSegment()
    main = SAPSegment()

    name = directive.name

    if name == "comm":
        lbl = directive.args[0]
        size = directive.args[1]

        main.write_label(lbl)
        main.write_directive("allocate", "#"+size)
    elif name == "word":
        size = meta.wordsize
        value = int(directive.args[0])
        
        main.write_seg(intvalue(size, value))
    elif name == "byte":
        main.write_directive("integer", "#"+directive.args[0])
    elif name == "zero":
        size = directive.args[0]
        
        main.write_directive("allocate", "#"+size)
    else:
        if comment_unused: main.write_comment("[AVR] "+directive.raw)
        
    return main, header
