import re
from .arguments import arg_to_register

def compare_args(a, b):
    insertion = []
    insertion.append("push r1")
    insertion.append("push r2")
    insertion+=arg_to_register(a, 1)
    insertion+=arg_to_register(b, 2)
    insertion.append("cmprr r1 r2")
    insertion.append("pop r2")
    insertion.append("pop r1")
    return insertion

class Branch:
    def __init__(self):
        self.condition = None
        self.blocks = []
    def add_block(self, b):
        self.blocks.append(b)

def parse_if_chunks(_lines):
    chunks = []
    branch = Branch()
    bnblock = []
    nest = 0
    for line in _lines:
        if nest == 1:
            if line.strip().startswith("else"):
                branch.add_block(bnblock)
                bnblock = []
                # [None]
                # if line.strip().startswith("else if "):
                #     bnblock[0] = line
                
            elif line.strip().startswith("endif"):
                branch.add_block(bnblock)
                bnblock = []
            else:
                bnblock.append(line)
        if nest > 1:
            bnblock.append(line)

        if line.strip().startswith("if "):
            nest+=1
            if nest == 1:
                branch.condition = line
        if line.strip().startswith("endif"):
            nest-=1
            
            if nest == 0:
                chunks.append(branch)
                branch = Branch()
        elif nest == 0:
            chunks.append(line)
    return chunks

def convert_ifs(_lines, prefix=""):
    chunks = parse_if_chunks(_lines)
    lines = []
    branch_id = 0
    for chunk in chunks:
        if isinstance(chunk, Branch):
            condition = lcut(chunk.condition.strip(),"if").replace(" ", "")
            ops = ("==", ">", "<", "!=")
            
            parts = None
            for op in ops:
                if op in condition:
                    a,b = condition.split(op)
                    break
            
            iflabel = "bnIF"+prefix+str(branch_id)
            elselabel = "bnELSE"+prefix+str(branch_id)
            endiflabel = "bnEND"+prefix+str(branch_id)

            insertion = compare_args(a,b)
            if op == "==":
                insertion.append("jmpz "+iflabel)
                insertion.append("jmp "+elselabel)
            elif op == "!=":
                insertion.append("jmpne "+iflabel)
                insertion.append("jmp "+elselabel)
            elif op == ">":
                insertion.append("jmpn "+iflabel)
                insertion.append("jmp "+elselabel)
            elif op == "<":
                insertion.append("jmpp "+iflabel)
                insertion.append("jmp "+elselabel)
            elif op == ">=":
                insertion.append("jmpp "+elselabel)
                insertion.append("jmp "+iflabel)
            elif op == "<=":
                insertion.append("jmpn "+elselabel)
                insertion.append("jmp "+iflabel)
            else:
                print("Invalid operation",op)
                exit()
            
            insertion.append(iflabel+":")
            insertion+=convert_ifs(chunk.blocks[0], prefix+"Nest")
            insertion.append("jmp "+endiflabel)
            if len(chunk.blocks) > 1:
                insertion.append(elselabel+":")
                insertion+=convert_ifs(chunk.blocks[1], prefix+"Nest")
            else:
                insertion.append(elselabel+": nop")
            insertion.append(endiflabel+": nop")
            lines+=insertion
            branch_id+=1
        else:
            lines.append(chunk)
    return lines
