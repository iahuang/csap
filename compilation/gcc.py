import os
import subprocess

def _compile(path, optimization=1, pic=False):
    args = ["-O"+str(optimization), "-fno-asynchronous-unwind-tables"]
    # if not pic:
    #     args.append("-fno-pic")
    p = subprocess.run(["avr-gcc",
                        "-S",
                        path]+args)
    return p

def compile(prg, *args):
    cwd = os.getcwd()
    os.chdir("tmp")
    with open("tmp.c", "w") as fl:
        fl.write(prg)
    p = _compile("tmp.c", *args)

    if p.returncode != 0:
        print("GCC terminated with exit code "+str(p.returncode))
        exit()
    
    with open("tmp.s") as fl:
        return fl.read()
    
    os.chdir(cwd)