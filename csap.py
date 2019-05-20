import sys
import os
from termcolor import colored

from compilation import gcc

argv = sys.argv[1:]

if __name__ == "__main__":
    csrc_path = argv[0]
    
    with open(csrc_path) as fl:
        assembly = gcc.compile(fl.read())
    print(assembly)
