import os


class VMWriter:

    CONST = "constant"

    ADD = "add"
    SUB = "sub"
    NEG = "neg"

    def __init__(self, vm_file):
        self.vm_file = vm_file

    def write_push(self, segment, index):
        self.vm_file.write("push "+segment+" "+str(index)+"\n")

    def write_pop(self, segment, index):
        self.vm_file.write("pop "+segment+" "+str(index)+"\n")

    def write_arithmetic(self, arithmetic_func):
        self.vm_file.write(arithmetic_func+"\n")

    def write_label(self, label_name):
        self.vm_file.write("label " + label_name + "\n")

    def write_go_to(self, label):
        self.vm_file.write("goto "+label+"\n")

    def write_if(self, label):
        self.vm_file.write("if-goto "+label+"\n")

    def write_call(self, name, nargs):
        self.vm_file.write("call "+name+" "+str(nargs)+"\n")

    def write_function(self, name, nlocals):
        self.vm_file.write("function "+name+" "+str(nlocals)+"\n")

    def write_return(self):
        self.vm_file.write("return\n")

    def close(self):
        self.vm_file.close()