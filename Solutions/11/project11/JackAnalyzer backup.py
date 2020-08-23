import sys
import os
import Tokenizer
import VMWriter
import SymbolTable

# TEST let statements for arrays
# original ConvertToBin first do statement remains untested


class CompilationEngine:
    def __init__(self, token_stream, vm_writer, symbol_table):
        self.tree_depth = 0
        self.token_stream = token_stream
        self.vm_writer = vm_writer
        self.symbol_table = symbol_table
        self.class_name = ""
        self.while_counter = 0
        self.if_counter = 0

    def compile_class(self):
        self.token_stream.advance()
        self.token_stream.advance()
        self.class_name = self.token_stream.identifier()
        self.token_stream.advance()
        while self.token_stream.hasMoreTokens():
            self.token_stream.advance()
            if self.token_stream.tokenType() == "keyword":
                if (self.token_stream.keyWord() == "static") | (self.token_stream.keyWord() == "field"):
                    self.compile_class_var_dec()
                else:  # subroutineDec
                    self.compile_subroutine()
            else:
                break  # unnecessary?

    def compile_class_var_dec(self):
        kind = self.token_stream.keyWord()
        self.token_stream.advance()
        if self.token_stream.tokenType() == "keyword":
            var_type = self.token_stream.keyWord()
        else:
            var_type = self.token_stream.identifier()
        self.token_stream.advance()
        name = self.token_stream.identifier()
        self.symbol_table.define(name, var_type, kind)
        self.token_stream.advance()
        while self.token_stream.symbol() == ",":
            self.token_stream.advance()
            name = self.token_stream.identifier()
            self.symbol_table.define(name, var_type, kind)
            self.token_stream.advance()

    def compile_subroutine(self):
        self.symbol_table.start_subroutine()
        subroutine_kind = self.token_stream.keyWord()
        self.token_stream.advance()
        self.token_stream.advance()
        subroutine_name = self.class_name+"."+self.token_stream.identifier()
        self.token_stream.advance()
        self.token_stream.advance()
        self.compile_parameter_list()
        self.token_stream.advance()
        self.token_stream.advance()
        num_of_local_args = 0
        while self.token_stream.keyWord() == "var":
            num_of_local_args += self.compile_var_dec()
        self.vm_writer.write_function(subroutine_name, num_of_local_args)

        if subroutine_kind != "function":
            self.symbol_table.define("this", self.class_name, "arg")
        if subroutine_kind == "constructor":
            fields = self.symbol_table.var_count("field")
            self.vm_writer.write_push("constant", fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
            self.vm_writer.write_push("pointer", 0)
        if subroutine_kind == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        self.compile_statements()  # statements

    def compile_parameter_list(self):
        if (self.token_stream.tokenType() == "symbol") & (self.token_stream.symbol() == ")"):
            return  # empty parameter list
        if self.token_stream.tokenType() == "keyword":
            var_type = self.token_stream.keyWord()
        else:
            var_type = self.token_stream.identifier()
        self.token_stream.advance()
        var_name = self.token_stream.identifier()
        self.symbol_table.define(var_name, var_type, SymbolTable.SymbolTable.ARG)
        self.token_stream.advance()
        while self.token_stream.symbol() == ",":
            self.token_stream.advance()
            if self.token_stream.tokenType() == "keyword":
                var_type = self.token_stream.keyWord()
            else:
                var_type = self.token_stream.identifier()
            self.token_stream.advance()
            var_name = self.token_stream.identifier()
            self.symbol_table.define(var_name, var_type, SymbolTable.SymbolTable.ARG)
            self.token_stream.advance()

    def compile_var_dec(self):
        number_of_local_arguments = 1
        self.token_stream.advance()
        if self.token_stream.tokenType() == "keyword":
            var_type = self.token_stream.keyWord()
        else:
            var_type = self.token_stream.identifier()
        self.token_stream.advance()
        var_name = self.token_stream.identifier()
        self.symbol_table.define(var_name, var_type, SymbolTable.SymbolTable.VAR)
        self.token_stream.advance()
        while self.token_stream.symbol() == ",":
            number_of_local_arguments += 1
            self.token_stream.advance()
            var_name = self.token_stream.identifier()
            self.symbol_table.define(var_name, var_type, SymbolTable.SymbolTable.VAR)
            self.token_stream.advance()
        self.token_stream.advance()
        return number_of_local_arguments

    def compile_statements(self):
        while (self.token_stream.hasMoreTokens()) & (self.token_stream.tokenType() == "keyword"):
            if self.token_stream.keyWord() == "let":
                self.compile_let_statement()
            elif self.token_stream.keyWord() == "do":
                self.compile_do_statement()
            elif self.token_stream.keyWord() == "if":
                self.compile_if_statement()
            elif self.token_stream.keyWord() == "while":
                self.compile_while_statement(self.while_counter)
            else:
                self.compile_return_statement()

    def compile_let_statement(self):
        self.token_stream.advance()     # advance 'let'
        var_name = self.token_stream.identifier()
        self.token_stream.advance()     # advance the var
        if self.token_stream.symbol() == "[":
            self.token_stream.advance()     # advance '['
            self.vm_writer.write_push(self.symbol_table.kind_of(var_name), self.symbol_table.index_of(var_name))
            self.compile_expression()
            self.vm_writer.write_arithmetic(VMWriter.VMWriter.ADD)
            self.vm_writer.write_pop("pointer", "1")
            self.token_stream.advance()     # advance ']'
            self.token_stream.advance()     # advance '='
            self.compile_expression()
            self.vm_writer.write_pop("that", "0")  # smells like shit
        else:
            self.token_stream.advance()     # advance '='
            self.compile_expression()
            self.vm_writer.write_pop(self.symbol_table.kind_of(var_name), self.symbol_table.index_of(var_name))
        self.token_stream.advance()  # advance ';'

    def compile_if_statement(self):
        self.token_stream.advance()  # advancing the if token
        self.token_stream.advance()  # advancing the '(' token
        self.compile_expression()
        self.token_stream.advance()  # advance ')'
        self.token_stream.advance()  # advance '{'
        self.vm_writer.write_arithmetic("not")
        if_else_label_array = self.build_label("if")
        if_label = if_else_label_array[0]
        else_label = if_else_label_array[1]
        self.vm_writer.write_if(else_label)  # if-goto else_unique#
        self.compile_statements()
        self.token_stream.advance()  # advance '}'
        if self.token_stream.getToken() == "else":  # advance '}'
            self.vm_writer.write_go_to(if_label)
            self.token_stream.advance()  # advance else
            self.token_stream.advance()  # advance '{'
            self.vm_writer.write_label(else_label)
            self.compile_statements()
            self.vm_writer.write_label(if_label)
            self.token_stream.advance()  # advance '}'
        else:  # no else in jack code
            self.vm_writer.write_label(else_label)

    def build_label(self, kind):
        if kind == "if":
            if_count = self.if_counter
            self.if_counter += 1
            return ["if_" + str(if_count), "else_" + str(if_count)]

        elif kind == "while":
            while_count = self.while_counter
            self.while_counter += 1
            return "while_" + str(while_count)

    def compile_while_statement(self, while_number):
        self.while_counter += 1
        self.token_stream.advance()
        self.token_stream.advance()
        self.vm_writer.write_label("START_WHILE_"+str(while_number))
        self.compile_expression()
        self.vm_writer.write_if("DO_WHILE_"+str(while_number))
        self.vm_writer.write_go_to("END_WHILE_"+str(while_number))
        self.vm_writer.write_label("DO_WHILE_"+str(while_number))
        self.token_stream.advance()
        self.token_stream.advance()

        self.compile_statements()
        self.vm_writer.write_go_to("START_WHILE_"+str(while_number))
        self.vm_writer.write_label("END_WHILE_"+str(while_number))

        self.token_stream.advance()
        # ?self.token_stream.advance()

    def compile_do_statement(self):
        self.token_stream.advance()  # do
        self.compile_subroutine_call()
        self.token_stream.advance()

    def compile_return_statement(self):
        self.token_stream.advance()  # return
        if self.token_stream.symbol() == ";":
            self.vm_writer.write_push(VMWriter.VMWriter.CONST, 0)
            self.vm_writer.write_return()
            self.token_stream.advance()  # ;
            return
        self.compile_expression()
        self.vm_writer.write_return()
        self.token_stream.advance()  # ;

    def compile_subroutine_call(self):
        token = self.token_stream.identifier()
        if self.symbol_table.kind_of(token):  # an object's method call
            self.token_stream.advance()
            self.token_stream.advance()
            method_name = self.symbol_table.type_of(token) + "." + self.token_stream.identifier()
            self.vm_writer.write_push(self.symbol_table.kind_of(token), self.symbol_table.index_of(token))
            self.token_stream.advance()
            self.token_stream.advance()
            number_of_arguments = self.compile_expression_list() + 1
            self.token_stream.advance()
            self.vm_writer.write_call(method_name, number_of_arguments)
            print(method_name + str(number_of_arguments))
            return
        self.token_stream.advance()     #
        if self.token_stream.identifier() == ".":  # function call
            L0X = False
            self.token_stream.advance()
            func_name = token + "." + self.token_stream.identifier()
            if self.token_stream.identifier() == "new":
                L0X = True
            self.token_stream.advance()
            self.token_stream.advance()
            number_of_arguments = self.compile_expression_list()
            if L0X:
                number_of_arguments +=1
            self.token_stream.advance()
            self.vm_writer.write_call(func_name, number_of_arguments)

        else:  # a local method call
            method_name = self.class_name + "." + token
            self.vm_writer.write_push("pointer", 0)
            self.token_stream.advance()
            number_of_arguments = self.compile_expression_list() +1
            self.token_stream.advance()
            self.vm_writer.write_call(method_name, number_of_arguments)



    def compile_expression_list(self):
        number_of_args = 0
        if self.token_stream.getToken() == ")":
            return number_of_args
        number_of_args += 1
        self.compile_expression()
        while self.token_stream.symbol() == ",":
            self.token_stream.advance()
            number_of_args += 1
            self.compile_expression()
        return number_of_args

    def compile_unary_expression(self):
        if self.token_stream.getToken() == '~':
            self.token_stream.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic("not")
        elif self.token_stream.getToken() == '-':
            self.token_stream.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic("neg")
        else:
            print("something went wrong")

    def compile_term(self):
        current = self.token_stream.getToken()
        if self.token_stream.isInt():
            self.vm_writer.write_push(VMWriter.VMWriter.CONST, current)
            self.token_stream.advance()
        elif self.token_stream.tokenType() == Tokenizer.STRING_CONST:
            self.build_string(current)
            self.token_stream.advance()
        elif current == '(':
            self.token_stream.advance()     # advancing '('
            self.compile_expression()       # compiling expression inside ()
            self.token_stream.advance()     # advancing ')'
        elif current == "~" or current == "-":
            self.compile_unary_expression()
        elif self.symbol_table.kind_of(current):    # variable
            self.token_stream.advance()
            if self.token_stream.getToken == '[':  # if we have var[expression]
                self.vm_writer.write_push(self.symbol_table.kind_of(current), self.symbol_table.index_of(current))
                self.token_stream.advance()  # advance the '['
                self.compile_expression()
                self.token_stream.advance()  # advance the ']'
                self.vm_writer.write_arithmetic("add")
            elif self.token_stream.getToken == ".":
                self.token_stream.advance()     # advance '.'
                self.vm_writer.write_push(self.symbol_table.kind_of(current), self.symbol_table.index_of(current))
                method_name = self.symbol_table.type_of(current)
                method_name += "." + self.token_stream.getToken()
                self.token_stream.advance()     # advance func name
                self.token_stream.advance()     # advance '('
                num_args = self.compile_expression_list()+1      ## dont know if num of args should include this object
                self.vm_writer.write_call(method_name, num_args)
                self.token_stream.advance()     # advance ')'
            else:   # variable without func call or array index
                self.vm_writer.write_push(self.symbol_table.kind_of(current), self.symbol_table.index_of(current))
        elif current == "true":
            self.vm_writer.write_push(VMWriter.VMWriter.CONST, 1)
            self.vm_writer.write_arithmetic("neg")
            self.token_stream.advance()
        elif current == "false" or current == "null":
            self.vm_writer.write_push(VMWriter.VMWriter.CONST, 0)
            self.token_stream.advance()
        elif current == "this":
            self.vm_writer.write_push("pointer", 0)
            self.token_stream.advance()
        else:   # call
            subroutine_name = self.token_stream.getToken()
            self.token_stream.advance()
            if self.token_stream.getToken() == '.':
                L0X = False
                self.token_stream.advance()     # advancing '.'
                subroutine_name += "." + self.token_stream.getToken()
                if self.token_stream.getToken() == "new":
                    L0X = True
                self.token_stream.advance()     # advance the subroutine name
                self.token_stream.advance()     # advance '('
                num_args = self.compile_expression_list()
                if L0X:
                    num_args += 1
                self.vm_writer.write_call(subroutine_name, num_args)
            else:   # local method call
                method_name = self.class_name + "." + subroutine_name
                self.vm_writer.write_push("pointer", 0)     # push pointer 0
                self.token_stream.advance()     # advance '('
                num_args = self.compile_expression_list() + 1       ## dont know if num of args should include this object
                self.vm_writer.write_call(method_name, num_args)
            self.token_stream.advance()  # advance ')'

    def build_string(self, string):
        string_length = len(string)
        self.vm_writer.write_push(VMWriter.VMWriter.CONST, string_length)  # pushing the length of the string to the stack
        self.vm_writer.write_call("String.new", 1)                # constructing a string of the desired length
        for c in string:
            self.vm_writer.write_push(VMWriter.VMWriter.CONST, ord(c))     # pushing the ascii value of c to the stack
            self.vm_writer.write_call("String.appendChar", 1)     # appending the char to the string

    def compile_expression(self):
        self.compile_term()
        while self.token_stream.isop():
            operator = self.token_stream.getToken()
            self.token_stream.advance()
            self.compile_term()
            if operator == '+':
                self.vm_writer.write_arithmetic("add")
            elif operator == '-':
                self.vm_writer.write_arithmetic("sub")
            elif operator == '*':
                self.vm_writer.write_call("Math.multiply", 2)
            elif operator == '/':
                self.vm_writer.write_call("Math.divide", 2)
            elif operator == '&':
                self.vm_writer.write_arithmetic("and")
            elif operator == '|':
                self.vm_writer.write_arithmetic("or")
            elif operator == '&lt;':
                self.vm_writer.write_arithmetic("lt")
            elif operator == '&gt;':
                self.vm_writer.write_arithmetic("gt")
            elif operator == '=':
                self.vm_writer.write_arithmetic("eq")


def compile_file(jack_file_name, vm_file_name):
    jack_file = open(jack_file_name, 'r')
    tokenizer = Tokenizer.Tokenizer(jack_file)
    symbol_table = SymbolTable.SymbolTable()
    vm_file = open(vm_file_name, 'w')
    vm_writer = VMWriter.VMWriter(vm_file)
    compilation_engine = CompilationEngine(tokenizer, vm_writer, symbol_table)
    compilation_engine.compile_class()


def jack_compile():
    path = ""
    for argument in sys.argv:
        if argument != sys.argv[0]:
            path += argument + " "
    path = path[:-1]
    path = os.path.expanduser(path)
    print(path)
    if os.path.isdir(path):
        file_root = path + "/"
        for file in os.listdir(path):
            filename = os.path.splitext(file)
            if filename[1] == ".jack":
                vm_file_name = str(filename[0].split("/")[-1])
                vm_file_full_name = file_root + vm_file_name + ".vm"
                jack_file_name = file_root + file
                compile_file(jack_file_name, vm_file_full_name)
    else:
        filename = os.path.splitext(path)
        vm_file_name = filename[0] + ".vm"
        compile_file(path, vm_file_name)

jack_compile()
