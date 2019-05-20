"""
A VM for SAP written in Python. Lighter, more extensible, easier to write.
"""
import re
import os


class Reference:
    def __init__(self, cpu):
        self.cpu = cpu


class RegisterReference(Reference):
    def __init__(self, cpu, num):
        super().__init__(cpu)
        self.num = num

    @property
    def value(self):
        return self.cpu.reg[self.num]

    @value.setter
    def value(self, to):
        self.cpu.reg[self.num] = to


class MemoryReference(Reference):
    def __init__(self, cpu, addr):
        super().__init__(cpu)
        self.addr = addr

    @property
    def value(self):
        return self.cpu.get(self.addr)

    @value.setter
    def value(self, to):
        self.cpu.set(self.addr, to)


class ConstantReference(Reference):
    def __init__(self, cpu, num):
        super().__init__(cpu)
        self.num = num

    @property
    def value(self):
        return self.num

    @value.setter
    def value(self, to):
        print("Cannot set value of constant")
        exit()


class IndirectReference(Reference):
    def __init__(self, cpu, num):
        super().__init__(cpu)
        self.num = num

    @property
    def value(self):
        return self.cpu.get(self.cpu.reg[self.num])

    @value.setter
    def value(self, to):
        self.cpu.set(self.cpu.reg[self.num], to)


class CPU:
    def __init__(self, memsize):
        self.memory = list([0 for i in range(memsize)])
        self.reg = list([0 for i in range(10)])
        self.rpc = 0
        self.rcp = 0

        self.internal_stack = []

    def get(self, loc):
        return self.memory[loc]

    def set(self, loc, to):
        self.memory[loc] = to

    def push(self, x):
        self.internal_stack.append(x)

    def pop(self):
        return self.internal_stack.pop()

    def push_instruction(self, x):
        self.push(x.value)

    def pop_instruction(self, into):
        into.value = self.pop()

    def digest(self):
        self.rpc += 1
        return self.get(self.rpc)

    def next_reg(self):
        return RegisterReference(self, self.digest())

    def next_addr(self):
        return MemoryReference(self, self.digest())

    def next_const(self):
        return ConstantReference(self, self.digest())

    def next_ind(self):
        return IndirectReference(self, self.digest())

    def clr(self, target):
        target.value = 0

    def clrb(self, start, count):
        for offset in range(0, count.value):
            self.clr(MemoryReference(self, start.value+offset))

    def mov(self, src, dest):
        dest.value = src.value

    def movb(self, src, dest, count):
        for offset in range(0, count.value):
            self.set(dest.value+offset, self.get(src.value+offset))

    def add(self, qty, to):
        to.value += qty.value

    def sub(self, qty, frm):
        frm.value -= qty.value

    def mul(self, by, target):
        target.value *= by.value

    def div(self, into, target):
        target.value /= into.value

    def jmp(self, to):
        self.rpc = to-1

    def sojz(self, target, jump):
        target.value -= 1

        if target.value == 0:
            self.jmp(jump)

    def sojnz(self, target, jump):
        target.value -= 1

        if target.value != 0:
            self.jmp(jump)

    def aojz(self, target, jump):
        target.value += 1

        if target.value == 0:
            self.jmp(jump)

    def aojnz(self, target, jump):
        target.value += 1

        if target.value != 0:
            self.jmp(jump)

    def cmp(self, a, b):
        self.rcp = b.value-a.value

    def jmpn(self, to):
        if self.rcp < 0:
            self.jmp(to)

    def jmpp(self, to):
        if self.rcp > 0:
            self.jmp(to)

    def jmpz(self, to):
        if self.rcp == 0:
            self.jmp(to)

    def jmpne(self, to):
        if self.rcp != 0:
            self.jmp(to)

    def jsr(self, to):
        self.push(self.rpc+1)
        self.jmp(to)
        for reg_num in range(5, 10):
            self.push(self.reg[reg_num])

    def ret(self):
        for reg_num in range(5, 10)[::-1]:
            self.reg[reg_num] = self.pop()
        return_to = self.pop()
        self.jmp(return_to)

    def outc(self, char):
        print(chr(char.value), end="")

    def printi(self, num):
        print(num.value, end="")

    def outs(self, label):
        data_start = label.addr
        length = self.get(data_start)
        string_start = data_start+1

        result = ""
        for addr in range(string_start, string_start+length):
            result += chr(self.get(addr))
        print(result, end="")

    def nop(self):
        # hmmmmmmmmmmm
        return

    def run_iteration(self):
        opcode = self.digest()

        if opcode == 0:
            exit()
        elif opcode == 1:
            self.clr(self.next_reg())
        elif opcode == 2:
            self.clr(self.next_addr())
        elif opcode == 3:
            self.clr(self.next_addr())
        elif opcode == 4:
            self.clrb(self.next_reg(), self.next_reg())
        elif opcode == 5:
            self.mov(self.next_const(), self.next_reg())
        elif opcode == 6:
            self.mov(self.next_reg(), self.next_reg())
        elif opcode == 7:
            self.mov(self.next_reg(), self.next_addr())
        elif opcode == 8:
            self.mov(self.next_addr(), self.next_reg())
        elif opcode == 9:
            self.mov(self.next_ind(), self.next_reg())
        elif opcode == 10:
            self.mov(self.next_const(), self.next_reg())
        elif opcode == 11:
            self.movb(self.next_reg(), self.next_reg(), self.next_reg())
        elif opcode == 12:
            self.add(self.next_const(), self.next_reg())
        elif opcode == 13:
            self.add(self.next_reg(), self.next_reg())
        elif opcode == 14:
            self.add(self.next_addr(), self.next_reg())
        elif opcode == 15:
            self.add(self.next_ind(), self.next_reg())
        elif opcode == 16:
            self.sub(self.next_const(), self.next_reg())
        elif opcode == 17:
            self.sub(self.next_reg(), self.next_reg())
        elif opcode == 18:
            self.sub(self.next_addr(), self.next_reg())
        elif opcode == 19:
            self.sub(self.next_ind(), self.next_reg())
        elif opcode == 20:
            self.mul(self.next_const(), self.next_reg())
        elif opcode == 21:
            self.mul(self.next_reg(), self.next_reg())
        elif opcode == 22:
            self.mul(self.next_addr(), self.next_reg())
        elif opcode == 23:
            self.mul(self.next_ind(), self.next_reg())
        elif opcode == 24:
            self.div(self.next_const(), self.next_reg())
        elif opcode == 25:
            self.div(self.next_reg(), self.next_reg())
        elif opcode == 26:
            self.div(self.next_addr(), self.next_reg())
        elif opcode == 27:
            self.div(self.next_ind(), self.next_reg())
        elif opcode == 28:
            self.jmp(self.digest())
        elif opcode == 29:
            self.sojz(self.next_reg(),  self.digest())
        elif opcode == 30:
            self.sojnz(self.next_reg(),  self.digest())
        elif opcode == 31:
            self.aojz(self.next_reg(),  self.digest())
        elif opcode == 32:
            self.aojnz(self.next_reg(),  self.digest())
        elif opcode == 33:
            self.cmp(self.next_const(), self.next_reg())
        elif opcode == 34:
            self.cmp(self.next_reg(), self.next_reg())
        elif opcode == 35:
            self.cmp(self.next_addr(), self.next_reg())
        elif opcode == 36:
            self.jmpn(self.digest())
        elif opcode == 37:
            self.jmpz(self.digest())
        elif opcode == 38:
            self.jmpp(self.digest())
        elif opcode == 39:
            self.jsr(self.digest())
        elif opcode == 40:
            self.ret()
        elif opcode == 41:
            self.push_instruction(self.next_reg())
        elif opcode == 42:
            self.pop_instruction(self.next_reg())
        elif opcode == 43:
            self.stackc(self.next_reg())
        elif opcode == 44:
            self.outc(self.next_const())
        elif opcode == 45:
            self.outc(self.next_reg())
        elif opcode == 46:
            self.outc(self.next_ind())
        elif opcode == 49:
            self.printi(self.next_reg())
        elif opcode == 53:
            self.mov(self.next_reg(), self.next_ind())
        elif opcode == 54:
            self.mov(self.next_ind(), self.next_ind())
        elif opcode == 55:
            self.outs(self.next_addr())
        elif opcode == 56:
            self.nop()
        elif opcode == 57:
            self.jmpne(self.digest())
        elif opcode == 52:
            pass
        else:
            print("Illegal operation", opcode)
            exit()

        return opcode
    def run(self):
        while 1:
            self.run_iteration()


class Debugger:
    def __init__(self, cpu):
        self.labels = {}
        self.cpu = cpu

    def load_lst(self, lst):
        for line in lst.split("\n"):
            line = line.strip()
            if line == "" or line == "Symbol Table:":
                continue
            
            if re.match("\d+:", line):
                pass
            else:
                label, addr = line.split(" ")
                self.labels[label] = int(addr)
    
    def read_label(self, label):
        return self.cpu.get(self.labels[label])
    
    def label_addr(self, label):
        return self.cpu.get(self.labels[label])

    def print_label(self, label):
        print(label, self.read_label(label))

    def on_brk(self):
        self.print_label("eax")
        self.print_label("ebx")
        self.print_label("ecx")
        self.print_label("edx")
        self.print_label("esi")
        self.print_label("edi")
        self.print_label("esp")
        self.print_label("ebp")
        print("stack:",self.cpu.memory[self.read_label("esp"):])


class VM:
    def __init__(self, memsize):
        self.cpu = CPU(memsize)
        self.debugger = Debugger(self.cpu)

    def load_bin(self, bin):
        size = bin[0]
        entry = bin[1]-1
        bin = bin[2:]
        self.cpu.memory[:size] = bin
        self.cpu.rpc = entry

    def load_prg(self, path):
        lst = os.path.splitext(path)[0]+".lst"
        with open(lst) as fl:
            self.debugger.load_lst(fl.read())
        with open(path) as fl:
            bin = list([int(n) for n in fl.read().strip().split("\n")])
        self.load_bin(bin)

    def run_step(self):
        opcode = self.cpu.run_iteration()
        if opcode == 52:
            self.debugger.on_brk()

    def run(self):
        while 1:
            self.run_step()


vm = VM(1000)
vm.load_prg(
    "/Users/ianhuang/Documents/simple-assembly-programming/x86em/out.expanded.bin")
vm.run()
