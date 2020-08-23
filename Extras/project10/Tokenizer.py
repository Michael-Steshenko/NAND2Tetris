import os
import sys
import re

letterMatcher = re.compile("\\w")
firstLetterMatcher = re.compile("")


keywords = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'true', 'return'}

symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}

operators = {'+', '-', '*', '/', '&', '|', '&lt;', '&gt;', '='}

# Token types:
KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST \
    = "keyword", "symbol", "identifier", "integerConstant", "stringConstant"

class Tokenizer:
    current = [None, None];     # current[0] is the current token, current[1] is the token type

    def __init__(self, stream):
        self.stream = stream

    def hasMoreTokensRecursive(self, pointer):
        next = self.nextChar()  # read 1 byte (1 char in ASCII)
        if next:
            if next.isspace():
                pointer = self.stream.tell()
                return self.hasMoreTokensRecursive(pointer)
            else:   # move the stream pointer back 1 byte
                self.stream.seek(pointer)
                return True
        else:
            return False

    def hasMoreTokens(self):
        return self.hasMoreTokensRecursive(self.stream.tell())


    def advance(self):
        if self.hasMoreTokens():
            char = self.nextChar()  # gets the next char in the file white space is ignored because hasMoreTokens()
            if char.isupper() or char == '_':
                self.setToken(self.fetchWord(char))
                self.setTokenType(IDENTIFIER)
            elif char.islower():
                self.setToken(self.fetchWord(char))
                if self.getToken() in keywords:
                    self.setTokenType(KEYWORD)
                else:
                    self.setTokenType(IDENTIFIER)
            elif char in symbols:
                if char == "/" and self.checkCommnet():     # if it's a comment
                    self.advance()
                else:
                    self.setToken(char)
                    self.setTokenType(SYMBOL)
            elif char.isdigit():
                self.setToken(self.fetchIntConst(char))
                self.setTokenType(INT_CONST)
            elif char == "\"":
                self.setToken(self.fetchStringConst())
                self.setTokenType(STRING_CONST)
            else:
                print("something went wrong in advancing the tokenizer")
                print(char)
        else:
            print("no more tokens")

    def setToken(self, token):
        if token == "<":
            token = "&lt;"
        if token == ">":
            token = "&gt;"
        self.current[0] = token
        #print("setting token to: "+token)

    def setTokenType(self, tokenType):
        self.current[1] = tokenType

    def getToken(self):
        return self.current[0]

    def tokenType(self):
        return self.current[1]

    def nextChar(self):
        next = self.stream.read(1)
        if(next):
            #print(next)
            return next
        return False

    def fetchWord(self, startOfword):
        word = startOfword
        pointer = self.stream.tell()
        nextChar = self.nextChar()
        while nextChar and letterMatcher.fullmatch(nextChar):    # while there is a next char which is a letter
            #print("next char: "+nextChar)
            word += nextChar
            pointer = self.stream.tell()
            nextChar = self.nextChar()

        #self.stream.seek(self.stream.tell() - 1, 0)
        #print("acdc " + self.nextChar())
        #print("fucking word:" + word)

        self.stream.seek(pointer)
        return word

    def fetchIntConst(self, startOfNumber):
        number = startOfNumber
        pointer = self.stream.tell()
        nextChar = self.nextChar()
        while nextChar and nextChar.isdigit():    # while there is a next char which is a digit
            number += nextChar
            pointer = self.stream.tell()
            nextChar = self.nextChar()
        self.stream.seek(pointer)
        return number

    def fetchStringConst(self):
        string = ""
        nextChar = self.nextChar()
        while nextChar != "\"":
            string += nextChar
            nextChar = self.nextChar()
        return string

    def keyWord(self):
        return self.getToken()

    def symbol(self):
        return self.getToken()

    def identifier(self):
        return self.getToken()

    def intVal(self):
        return self.getToken()

    def stringVal(self):
        return self.getToken()

    def isop(self):
        if self.getToken() in operators:
            return True
        return False


    def checkCommnet(self):
        char = self.nextChar()
        if char == "/":
            self.skipLineComment()
            return True
        elif char == "*":
            self.skipMultylineComment()
            return True
        else:   # this means this is not a comment
            self.stream.seek(self.stream.tell() - 1, 0)
            return False


    def skipLineComment(self):
        while(self.nextChar() != "\n"):
            continue


    def skipMultylineComment(self):
        foundkohavit = False
        nextChar = self.nextChar()
        while (nextChar):
            if nextChar == "*":
                foundkohavit = True
            elif nextChar == "/" and foundkohavit is True:
                return
            else:       # next char is not "*"
                foundkohavit = False
            nextChar = self.nextChar()

    def __repr__(self):
        return("token: " + self.getToken() + " token type: "+self.tokenType())


def compile_file(jack_file_name, xml_file_name):
    # print("Starting compilation.\nSource file: "+jack_file_name+"\nDestination file: "+xml_file_name+"\n")
    jack_file = open(jack_file_name, 'r')

    tokenizer = Tokenizer(jack_file)

    for i in range(200):
        tokenizer.advance()
        print(tokenizer)
    xml_file = open(xml_file_name, 'w')

"""
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
"""