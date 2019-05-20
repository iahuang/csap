import subprocess
import sys
from termcolor import colored
from assembly.conversion import x86toSAP
import os
from sapplus import preprocess

argv = sys.argv[1:]


def gcc_compile(path, optimization=1, pic=False):
    args = ["-O"+str(optimization), "-fno-asynchronous-unwind-tables"]
    if not pic:
        args.append("-fno-pic")
    p = subprocess.run(["gcc",
                        "-S",
                        "-m32",
                        "-masm=intel",
                        path]+args)
    return p

def clang_compile(path, optimization=1, pic=False):
    args = ["-O"+str(optimization), "-fno-asynchronous-unwind-tables"]
    if not pic:
        args.append("-fno-pic")
    p = subprocess.run(["clang",
                        "-S",
                        "-m32",
                        "-mllvm",
                        "--x86-asm-syntax=intel",
                        path]+args)
    return p

def run():
    src_path = argv[0]
    optimization = 2
    for arg in argv:
        if arg.startswith("-O"):
            optimization = arg[2:]
    p = gcc_compile(src_path, optimization=optimization, pic=not "-nopic" in argv)
    if p.returncode != 0:
        print("GCC terminated with exit code "+str(p.returncode))
        exit(0)

    asm_path = os.path.splitext(src_path)[0]+'.s'

    with open("sap/x86.sap") as fl:
        header = fl.read()

    converter = x86toSAP(header)
    with open(asm_path) as fl:
        output = converter.convert(fl.read())

        print(output)
    
    with open("out.sap", "w") as fl:
        fl.write(output)

if __name__ == "__main__":
    run()
