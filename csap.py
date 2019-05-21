import sys
import os
from termcolor import colored

from compilation import gcc
from avrsap.translator import Translator
from assembler.assemble import assemble

argv = sys.argv[1:]

if __name__ == "__main__":
    csrc_path = argv[0]
    
    with open(csrc_path) as fl:
        avr_code = gcc.compile(fl.read())

    translator = Translator()
    sap = translator.to_sap(avr_code)

    with open("build/build.sap", "w") as fl:
        fl.write(sap)
        
    out = assemble(sap)

    if out.success:
        pass
    else:
        print("SAP output did not compile successfully")
