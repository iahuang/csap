from .sap import SAPSegment
from .util import parse_dsv

def token_to_ptr(token, reg_num):
    reg = "r"+str(reg_num)
    seg = SAPSegment()

    if token.type == "register":
        seg.write_inst("movar", "registers", reg)
        seg.write_inst("addir", f"#{token.reg_num}", reg)
    elif token.type == "memory":
        parts = parse_dsv(token.text, ["+", "-"])
        label = parts[0]
        seg.write_inst("movar", label, reg)
        if len(parts) != 1:
            op = parts[1]
            offset = parts[2]
            
            if op == "+":
                seg.write_inst("addir", f"#{offset}", reg)
            elif op == "-":
                seg.write_inst("subir", f"#{offset}", reg)
            else:
                print("Unsuported operation",op)

    else:
        print("Invalid addressing mode: pointer to",token.type)
        exit()

    return seg

def token_to_value(token, reg_num):
    seg = SAPSegment()
    reg = "r"+str(reg_num)
    if token.type == "register":
        seg.write_inst("movar", "registers", reg)
        seg.write_inst("addir", f"#{token.reg_num}", reg)
        seg.write_inst("movxr", reg, reg)
    elif token.type == "constant":
        seg.write_inst("movir", f"#{token.text}", reg)
    elif token.type == "memory":
        seg.write_seg(token_to_ptr(token, reg_num))
        seg.write_inst("movxr", reg, reg)

    return seg