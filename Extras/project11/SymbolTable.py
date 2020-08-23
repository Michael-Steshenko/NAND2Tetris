
class Identifier:

    def __init__(self, identifier_type, kind, index):
        self.type = identifier_type
        self.kind = kind
        self.index = index

    def __repr__(self):
        return "Identifier Object. type="+self.type+" kind="+self.kind+" index="+str(self.index)

    def get_kind(self):
        return self.kind

    def get_type(self):
        return self.type

    def get_index(self):
        return self.index


class SymbolTable:

    STATIC = "static"
    FIELD = "field"
    ARG = "arg"
    VAR = "var"

    LCL = "local"
    ARGUMENT = "argument"

    def __init__(self):
        self.global_symbols = dict()
        self.method_symbols = dict()
        self.static_index = 0
        self.field_index = 0
        self.arg_index = 0
        self.var_index = 0

    def start_subroutine(self):
        self.method_symbols = dict()
        self.arg_index = 0
        self.var_index = 0

    def define(self, name, identifier_type, kind):
        # Creating an identifier object
        if kind == self.STATIC:
            identifier = Identifier(identifier_type, kind, self.static_index)
            if name not in self.global_symbols:
                self.static_index += 1
            self.global_symbols[name] = identifier
        elif kind == self.FIELD:
            identifier = Identifier(identifier_type, "this", self.field_index)
            if name not in self.global_symbols:
                self.field_index += 1
            self.global_symbols[name] = identifier
        elif kind == self.ARG:
            identifier = Identifier(identifier_type, self.ARGUMENT, self.arg_index)
            if name not in self.method_symbols:
                self.arg_index += 1
            self.method_symbols[name] = identifier
        else:  # kind == var
            identifier = Identifier(identifier_type, self.LCL, self.var_index)
            if name not in self.method_symbols:
                self.var_index += 1
            self.method_symbols[name] = identifier
        # print(self.method_symbols)

    def var_count(self, kind):
        if kind == self.STATIC:
            return self.static_index
        elif kind == self.FIELD:
            return self.field_index
        elif kind == self.ARG:
            return self.arg_index
        else:  # kind == var
            return self.var_index

    def kind_of(self, name):
        if name in self.method_symbols:
            return self.method_symbols[name].get_kind()
        elif name in self.global_symbols:
            return self.global_symbols[name].get_kind()
        else:  # identifier not in scope
            return None

    def type_of(self, name):
        if name in self.method_symbols:
            return self.method_symbols[name].get_type()
        else:  # name in self.global_symbols
            return self.global_symbols[name].get_type()

    def index_of(self, name):
        if name in self.method_symbols:
            return self.method_symbols[name].get_index()
        else:  # name in self.global_symbols
            return self.global_symbols[name].get_index()
