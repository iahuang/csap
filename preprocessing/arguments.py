import re

def arg_to_register(arg, reg_num):
    insertion = []
    
    if re.fullmatch("r\d+", arg):  # Pass register as argument
        insertion.append(f"movrr {arg} r{reg_num}")

    elif arg.startswith('#'):  # Pass integer constant as argument
        insertion.append(f"movir {arg} r{reg_num}")
    elif arg.startswith("*"):  # Pass dereferenced value as argument
        arg = arg[1:]
        if re.match("r\d+", arg):  # Pass value of pointer register
            insertion.append(f"movrr {arg} r{reg_num}")
        else:  # Pass value of label
            insertion.append(f"movar {arg} r{reg_num}")
        insertion.append(f"movxr r{reg_num} r{reg_num}")
    elif arg.startswith("&"):  # Pass pointer to label as argument
        arg = arg[1:]
        insertion.append(f"movar {arg} r{reg_num}")
    else:
        print(
            f"{arg} is not a valid argument. If you're passing a label, you need to pass as its address or dereference it")
        exit()
    return insertion