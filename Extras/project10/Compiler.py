import sys
import os
import re
import Tokenizer

""" Global variables """
letterMatcher = re.compile("\\w")
firstLetterMatcher = re.compile("")
keywords = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'true'}
symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}

""" Constants """
# Token types:
KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST \
    = "keyword", "symbol", "identifier", "integerConstant", "stringConstant"


class CompilationEngine:
    def __init__(self, token_stream, xml_file):
        self.tree_depth = 0
        self.token_stream = token_stream
        self.destination_file = xml_file

    def xml_terminal_out(self, tag, content):
        self.destination_file.write(self.tree_depth*"  "+"<"+tag+"> "+content+" </"+tag+">\n")

    def xml_non_terminal_out(self, tag, recursive_element):
        self.destination_file.write(self.tree_depth*"  "+"<"+tag+">\n")
        self.tree_depth += 1
        recursive_element()
        self.tree_depth -= 1
        self.destination_file.write(self.tree_depth*"  "+"</"+tag+">\n")

    def compile_class(self):
        self.destination_file.write(self.tree_depth*"  "+"<class>\n")  # <class>
        self.tree_depth += 1
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        assert self.token_stream.tokenType() == "keyword"
        assert self.token_stream.keyWord() == "class"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())  # <keyword> class </keyword>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        assert self.token_stream.tokenType() == "identifier"
        class_name = self.token_stream.identifier()
        self.xml_terminal_out(self.token_stream.tokenType(), class_name)  # <identifier> class_name </identifier>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        assert self.token_stream.tokenType() == "symbol"
        opening_parenthesis = self.token_stream.symbol()
        self.xml_terminal_out(self.token_stream.tokenType(), opening_parenthesis)  # <symbol> { </symbol>
        while self.token_stream.hasMoreTokens():  # *modified from hasnext()
            self.token_stream.advance()
            if self.token_stream.tokenType() == "keyword":
                if (self.token_stream.keyWord() == "static") | (self.token_stream.keyWord() == "field"):
                    self.xml_non_terminal_out("classVarDec", self.compile_class_var_dec)
                    # <classVarDec>...</classVarDec>
                else:  # <subroutineDec>...</subroutineDec>
                    self.xml_non_terminal_out("subroutineDec", self.compile_subroutine)
            else:
                assert self.token_stream.tokenType() == "symbol"
                closing_parenthesis = self.token_stream.symbol()
                self.xml_terminal_out(self.token_stream.tokenType(), closing_parenthesis)  # <symbol> } </symbol>
                break  # unnecessary
        self.tree_depth -= 1
        self.destination_file.write(self.tree_depth*"  "+"</class>\n")  # </class>

    def compile_class_var_dec(self):
        assert self.token_stream.tokenType() == "keyword"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())
        # <keyword> static / field </keyword>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        self.compile_type()
        # return type: <keyword> type </keyword> if primitive. else: <identifier> type </identifier>
        assert self.token_stream.tokenType() == "identifier"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
        # <identifier> varName </identifier>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        assert self.token_stream.tokenType() == "symbol"
        while (self.token_stream.tokenType() == "symbol") & (self.token_stream.symbol() == ","):
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> , </symbol>
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()
            assert self.token_stream.tokenType() == "identifier"
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
            # <identifier> varName </identifier>
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()
        assert self.token_stream.tokenType() == "symbol"
        assert self.token_stream.symbol() == ";"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ; </symbol>

    def compile_type(self):
        if self.token_stream.tokenType() == "keyword":
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())
            # if primitive: <keyword> type </keyword>
        else:
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
            #  if not primitive: <identifier> type </identifier>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()

    def compile_subroutine(self):
        assert self.token_stream.tokenType() == "keyword"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())
        # <keyword> subroutineType </keyword> (constructor / function / method)
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        self.compile_type()
        # return type: <keyword> type </keyword> if primitive. else: <identifier> type </identifier>
        assert self.token_stream.tokenType() == "identifier"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
        # <keyword> subroutineName </keyword>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        assert self.token_stream.tokenType() == "symbol"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ( </symbol>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        self.xml_non_terminal_out("parameterList", self.compile_parameter_list)
        # <parameterList> ... </parameterList>
        assert self.token_stream.tokenType() == "symbol"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ) </symbol>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        self.xml_non_terminal_out("subroutineBody", self.compile_subroutine_body)

    def compile_parameter_list(self):
        if (self.token_stream.tokenType() == "symbol") & (self.token_stream.symbol() == ")"):
            return  # empty parameter list
        self.compile_type()
        # parameter type: <keyword> type </keyword> if primitive. else: <identifier> type </identifier>
        assert self.token_stream.tokenType() == "identifier"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
        # <identifier> varName </identifier>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        while (self.token_stream.tokenType() == "symbol") & (self.token_stream.symbol() == ","):
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> , </symbol>
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()
            self.compile_type()
            # parameter type: <keyword> type </keyword> if primitive. else: <identifier> type </identifier>
            assert self.token_stream.tokenType() == "identifier"
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
            # <identifier> varName </identifier>
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()

    def compile_subroutine_body(self):
        assert self.token_stream.tokenType() == "symbol"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> { </symbol>
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        while self.token_stream.keyWord() == "var":
            self.xml_non_terminal_out("varDec", self.compile_class_var_dec)  # <varDec> ... </varDec>
            self.token_stream.advance()
        self.xml_non_terminal_out("statements", self.compile_statements)  # <statements> ... </statements>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> } </symbol>

    def compile_var_dec(self):
        assert self.token_stream.tokenType() == "keyword"
        while self.token_stream.keyWord() == "var":
            self.compile_class_var_dec()
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())  # var
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        self.compile_type()  # type
        assert self.token_stream.tokenType() == "identifier"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())  # varName
        assert self.token_stream.hasMoreTokens()
        self.token_stream.advance()
        assert self.token_stream.tokenType() == "symbol"
        while (self.token_stream.tokenType() == "symbol") & (self.token_stream.symbol() == ","):
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # ,
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()
            assert self.token_stream.tokenType() == "identifier"
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())  # varName
            assert self.token_stream.hasMoreTokens()
            self.token_stream.advance()
        assert self.token_stream.tokenType() == "symbol"
        assert self.token_stream.symbol() == ";"
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # ;

    def compile_statements(self):
        # possibly change the while condition to be more restricting, as in match only to LET, DO, IF, WHILE
        while (self.token_stream.hasMoreTokens()) & (self.token_stream.tokenType() == "keyword"):
            assert self.token_stream.tokenType() == "keyword"
            if self.token_stream.keyWord() == "let":
                self.xml_non_terminal_out("letStatement", self.compile_let_statement)  # <letS..> ... </letS..>
            elif self.token_stream.keyWord() == "do":
                self.xml_non_terminal_out("doStatement", self.compile_do_statement)  # <doS..> ... </doS..>
            elif self.token_stream.keyWord() == "if":
                self.xml_non_terminal_out("ifStatement", self.compile_if_statement)  # <ifS..> ... </ifS..>
            elif self.token_stream.keyWord() == "while":
                self.xml_non_terminal_out("whileStatement", self.compile_while_statement)  # <whileS..> ... </whileS..>
            else:
                self.xml_non_terminal_out("returnStatement", self.compile_return_statement)
                # <returnS..> ... </returnS..>

    def compile_let_statement(self):
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())  # <keyword> let </keyword>
        self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())  # <keyword> var </keyword>
        self.token_stream.advance()
        if self.token_stream.symbol() == "[":
            self.xml_terminal_out(self.token_stream.tokenType(),
                                  self.token_stream.symbol())  # <symbol> [ </symbol>
            self.token_stream.advance()
            self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
            self.xml_terminal_out(self.token_stream.tokenType(),
                                  self.token_stream.symbol())  # <symbol> ] </symbol>
            self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> = </symbol>
        self.token_stream.advance()
        self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ; </symbol>
        self.token_stream.advance()

    def compile_if_statement(self):
        self.xml_terminal_out(self.token_stream.tokenType(),
                              self.token_stream.keyWord())  # <keyword> if </keyword>
        self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ( </symbol>
        self.token_stream.advance()
        self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ) </symbol>
        self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> { </symbol>
        self.token_stream.advance()
        self.xml_non_terminal_out("statements", self.compile_statements)  # <statements> ... </statements>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> } </symbol>
        self.token_stream.advance()
        if self.token_stream.keyWord() == "else":
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())
            # <keyword> if </keyword>
            self.token_stream.advance()
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> { </symbol>
            self.token_stream.advance()
            self.xml_non_terminal_out("statements", self.compile_statements)  # <statements> ... </statements>
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> } </symbol>
            self.token_stream.advance()

    def compile_while_statement(self):
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())  # <keyword> while </keyword>
        self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ( </symbol>
        self.token_stream.advance()
        self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ) </symbol>
        self.token_stream.advance()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> { </symbol>
        self.token_stream.advance()
        self.xml_non_terminal_out("statements", self.compile_statements)  # <statements> ... </statements>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> } </symbol>
        self.token_stream.advance()

    def compile_do_statement(self):
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())  # <keyword> do </keyword>
        self.token_stream.advance()
        self.compile_subroutine_call()
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ; </symbol>
        self.token_stream.advance()

    def compile_return_statement(self):
        print(self.token_stream.keyWord())
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())  # <keyword> return </keyword>
        self.token_stream.advance()
        print(self.token_stream.keyWord())
        if self.token_stream.symbol() == ";":
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ; </symbol>
            self.token_stream.advance()
            return
        self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> ; </symbol>
        self.token_stream.advance()

    def compile_expression(self):
        self.xml_non_terminal_out("term", self.compile_term)  # <term> ... </term>
        while self.token_stream.isop():
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # <symbol> op </symbol>
            self.token_stream.advance()
            self.xml_non_terminal_out("term", self.compile_term)  # <term> ... </term>

    def compile_term(self):
        if self.token_stream.tokenType() == "integerConstant":  # int
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.intVal())
            self.token_stream.advance()
        elif self.token_stream.tokenType() == "stringConstant":  # string
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.stringVal())
            self.token_stream.advance()
        elif self.token_stream.tokenType() == "keyword":  # consider making this condition true, false, null or this
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.keyWord())
            self.token_stream.advance()
        elif self.token_stream.tokenType() == "identifier":  # other options as described in comments
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
            # var / var in array / local subroutine / other subroutine
            self.token_stream.advance()
            if self.token_stream.symbol() == "[":  # array item
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # [
                self.token_stream.advance()
                self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # ]
                self.token_stream.advance()
            elif self.token_stream.symbol() == "(":  # local subroutine
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # (
                self.token_stream.advance()
                self.xml_non_terminal_out("expressionList", self.compile_expression_list)
                # <expressionList> ... </expressionList>
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # )
                self.token_stream.advance()
            elif self.token_stream.symbol() == ".":  # subroutine from a different class
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # .
                self.token_stream.advance()
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())  # subroutine name
                self.token_stream.advance()
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # (
                self.token_stream.advance()
                self.xml_non_terminal_out("expressionList", self.compile_expression_list)
                # <expressionList> ... </expressionList>
                self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # )
                self.token_stream.advance()
        elif self.token_stream.symbol() == "(":
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # (
            self.token_stream.advance()
            self.xml_non_terminal_out("expression", self.compile_expression)
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # )
            self.token_stream.advance()
        else:  # unary op term
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # UNARY OPERATOR
            self.token_stream.advance()

    def compile_subroutine_call(self):
        self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())
        self.token_stream.advance()
        if self.token_stream.symbol() == "(":  # local subroutine
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # (
            self.token_stream.advance()
            self.xml_non_terminal_out("expressionList", self.compile_expression_list)
            # <expressionList> ... </expressionList>
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # )
        else:  # subroutine from a different class
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # .
            self.token_stream.advance()
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.identifier())  # subroutine name
            self.token_stream.advance()
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # (
            self.token_stream.advance()
            self.xml_non_terminal_out("expressionList", self.compile_expression_list)
            # <expressionList> ... </expressionList>
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())  # )
        self.token_stream.advance()

    def compile_expression_list(self):
        if self.token_stream.symbol() == ")":
            return
        self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>
        while self.token_stream.symbol() == ",":
            self.xml_terminal_out(self.token_stream.tokenType(), self.token_stream.symbol())
            self.token_stream.advance()
            self.xml_non_terminal_out("expression", self.compile_expression)  # <expression> ... </expression>


def compile_file(jack_file_name, xml_file_name):
    # print("Starting compilation.\nSource file: "+jack_file_name+"\nDestination file: "+xml_file_name+"\n")
    jack_file = open(jack_file_name, 'r')
    tokenizer = Tokenizer.Tokenizer(jack_file)
    xml_file = open(xml_file_name, 'w')
    compilation_engine = CompilationEngine(tokenizer, xml_file)
    compilation_engine.compile_class()


def jack_compile():
    path = os.path.expanduser(sys.argv[1])
    if os.path.isdir(path):
        file_root = path + "/"
        for file in os.listdir(path):
            filename = os.path.splitext(file)
            if filename[1] == ".jack":
                xml_file_name = str(filename[0].split("/")[-1])
                xml_file_full_name = file_root + xml_file_name + ".xml"
                jack_file_name = file_root + file
                compile_file(jack_file_name, xml_file_full_name)
    else:
        filename = os.path.splitext(path)
        xml_file_name = filename[0] + ".xml"
        compile_file(path, xml_file_name)

jack_compile()
