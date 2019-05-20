from .arguments import arg_to_register
import re

class SAPMacro:
    def __init__(self):
        self.preserve_indentation = True
        self.match = ".+"
        self.debug_comment = True
        self.header_insertion = None

    def on_readline(self, line):
        pass


class AssignMacro(SAPMacro):
    def __init__(self):
        super().__init__()
        self.match = "\w+ ?="

    def on_readline(self, line):
        insertion = []
        parts = line.split("=")
        var = parts[0].strip()
        value = parts[1].strip()

        assign_to_reg = False
        output_reg = 1

        if re.match("r\d+", var):
            assign_to_reg = True
            output_reg = var.strip("r")
        else:
            insertion.append("push r"+str(output_reg))

        insertion+=arg_to_register(value, output_reg)

        if not assign_to_reg:
            insertion.append(f"movrm r{output_reg} {var}")
            insertion.append(f"pop r{output_reg}")
        return insertion


class PrintMacro(SAPMacro):
    def __init__(self):
        super().__init__()
        self.match = "print "
        self.str_count = 0

    def on_readline(self, line):
        self.header_insertion = []
        insertion = []

        parts = parse_dsv(line,[" "])[::2]
        args = parts[1:]

        for arg in args:
            if re.match('".+"', arg):
                tmp_label = "STRTMP"+str(self.str_count)
                self.str_count += 1

                self.header_insertion.append(f'{tmp_label}: .string {arg}')
                insertion.append("outs "+tmp_label)
            else:
                insertion.append("push r1")
                insertion+=arg_to_register(arg, 1)
                insertion.append("printi r1")
                insertion.append("pop r1")


            insertion.append("outci #32")
        insertion = insertion[:-1]
        return insertion


class PrintlnMacro(PrintMacro):
    def __init__(self):
        super().__init__()
        self.match = "println"
        self.str_count = 0

    def on_readline(self, line):
        insertion = super().on_readline(line)
        insertion.append("outci #10")
        return insertion


class CallMacro(SAPMacro):
    def __init__(self):
        super().__init__()
        self.match = "call"

    def on_readline(self, line):
        insertion = []

        instruction = line.strip()
        subroutine = instruction.split(" ")[1]
        args = instruction.split(" ")[2:]

        should_pop = []

        arg_num = 1
        for arg in args:
            if arg_num == 5:
                print("SAP supports a maximum of 4 arguments to subroutines")
                exit()
            insertion.append(f"push r{arg_num}")
            if re.fullmatch("r\d+", arg):  # Pass register as argument
                insertion.append(f"movrr {arg} r{arg_num}")

            elif arg.startswith('#'):  # Pass integer constant as argument
                insertion.append(f"movir {arg} r{arg_num}")
            elif arg.startswith("*"):  # Pass dereferenced value as argument
                arg = arg[1:]
                if re.match("r\d+", arg):  # Pass value of pointer register
                    insertion.append(f"movrr {arg} r{arg_num}")
                else:  # Pass value of label
                    insertion.append(f"movar {arg} r{arg_num}")
                insertion.append(f"movxr r{arg_num} r{arg_num}")
            elif arg.startswith("&"):  # Pass pointer to label as argument
                arg = arg[1:]
                insertion.append(f"movar {arg} r{arg_num}")
            else:
                print(
                    f"{arg} is not a valid argument. If you're passing a label, you need to pass as its address or dereference it")
                exit()
            should_pop.append(arg_num)
            arg_num += 1
        insertion.append(f"jsr {subroutine}")
        while should_pop:
            insertion.append(f"pop r{should_pop.pop()}")

        return insertion

def apply_macro(T: type, _lines):
    macro = T()
    header = []
    lines = _lines[:]
    for i, line in enumerate(_lines):
        if not re.match(macro.match, line.strip()):
            continue

        insertion = macro.on_readline(line.strip())

        if macro.header_insertion:
            header += macro.header_insertion

        if macro.debug_comment:
            insertion[0] += " ; "+line.strip()

        if macro.preserve_indentation and line.lstrip() != line:
            for j, new_line in enumerate(insertion):
                insertion[j] = "    "+new_line.strip()

        lines[i] = "\n".join(insertion)

    return header+lines