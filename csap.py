import sys
import os
from termcolor import colored

from compilation import gcc
from avrsap.translator import Translator
from assembler.assemble import assemble
from preprocessing.preprocessor import Preprocessor

argv = sys.argv[1:]

if __name__ == "__main__":
    csrc_path = argv[0]
    
    with open(csrc_path) as fl:
        avr_code = gcc.compile(fl.read())

    with open("lib/avrheader.sap") as fl:
        avrheader = fl.read()

    translator = Translator(avrheader)
    sap = translator.to_sap(avr_code)

    with open("build/build.sap.superset", "w") as fl:
        fl.write(sap)

    proc = Preprocessor()
    proc.load_extension("ext/sapplus.json")

    sap = proc.preprocess(sap)

    with open("build/build.sap", "w") as fl:
        fl.write(sap)
    
    out = assemble(sap)

    if out.success:
        pass
    else:
        print("SAP output did not compile successfully")
