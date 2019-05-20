def simple_macro_runner(insertion, argnames, args):
    insertion = insertion[:]
    for i, line in enumerate(insertion):
        for name, value in zip(argnames, args):
            insertion[i] = line.replace("$"+name, value)
            if "$"+name in line:
                break

    return insertion

class SimpleMacro(SAPMacro):
    def __init__(self, signature, insertion):
        super().__init__()
        self.insertion = insertion

        parts = signature.split(" ")
        self.name = parts[0]
        self.match = parts[0]
        self.argnames = parts[1:]

    def on_readline(self, line):
        line = line.strip()
        values = line.split(" ")[1:]
        return simple_macro_runner(self.insertion, self.argnames, values)


def simple_macro_type(signature, insertion):
    return lambda: SimpleMacro(signature, insertion)

def load_extension(json_data: str):
    macros = json.loads(json_data)
    macro_types = []

    for signature in macros:
        insertion = macros[signature]

        macro_types.append(simple_macro_type(signature, insertion))
    return macro_types