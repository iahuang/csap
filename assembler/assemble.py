import os
import subprocess
import re

def safe_rm(p):
    if os.path.exists(p):
        os.remove(p)


def clean_path(path):  # Stulin lazy
    if not path.endswith("/"):
        return path+"/"
    return path


def clean_output_files(project):
    safe_rm(project+".lst")
    safe_rm(project+".bin")
    safe_rm(project+".sym")

def get_errors(lst):
    offending_lines = re.findall(".+\n(?=\.{10})", lst)
    error_messages = re.findall(re.compile("^\.{10}.+$", re.MULTILINE), lst)
    return offending_lines, error_messages

def _assemble(prg, execpath="assembler/Assembler_OSX"):
    cwd = os.getcwd()
    os.chdir("tmp")
    clean_output_files("tmp")
    with open("tmp.txt", "w") as fl:
        fl.write(prg)
    
    p = subprocess.Popen([cwd+"/"+execpath], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    assembler_input = f'asm tmp\nquit'
    s = p.communicate(input=bytes(assembler_input, 'utf8'))
    os.chdir(cwd)
    return p

class AsmOutput:
    def __init__(self):
        self.success = False
        self.bin_content = None

        if os.path.exists("tmp/tmp.bin"):
            self.success = True

            with open("tmp/tmp.bin") as fl:
                self.bin_content = fl.read()

        with open("tmp/tmp.lst") as fl:
            self.lst_content = fl.read()
            

def assemble(prg, execpath="./assembler/Assembler_OSX"):
    p = _assemble(prg, execpath)
    if p.returncode != 0:
        print("Assembler returned non-zero error code "+str(p.returncode))
        exit()
    
    return AsmOutput()  