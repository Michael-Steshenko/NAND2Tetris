import sys
import os


""" CONSTANTS """
"""
# A constant representing the width of a word in RAM
CMD_LEN = 16
# Predefined symbols. These are the constants that will be used in assembly
SP = 0
LCL = 1
ARG = 2
THIS = 3
THAT = 4
SCREEN = 16384
KBD = 24576
# The last number of RAM to be reserved
RAM_RESERVE_END = 16
# A constant representing the first place in RAM available for variables
VAR_FIRST_MEM = 16
"""


""" Global variables"""
# A global variable representing the number of variables created in the
# supplied assembly code. When translating multiple files, this variable is
# set to 0 at the beginning of each translation process.
lt_calls = 0
gt_calls = 0
eq_calls = 0
func_calls = 0
g_filename = ""
g_current_func = ""
Recovery_Pointers = ["THAT", "THIS", "ARG", "LCL"]


def stack_push_rest(location, i):
    """receives string - a name of the location in memory which can be one of the following:
    argument, local, this, that, pointer, temp. and i a string representation pf the relative location from
    'location' argument"""
    return_string = "@//location\n" \
                    "D=M\n" \
                    "@//i\n" \
                    "A=D+A\n" \
                    "D=M\n" \
                    "@SP\n" \
                    "A=M\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M+1"

    location = determine_location(location)

    return_string = return_string.replace("//location", location)
    return_string = return_string.replace("//i", i)

    return return_string


def stack_push_static(i):
    varName = build_static_var_name(i)
    return_string = "@//varName\n" \
                    "D=M\n" \
                    "@SP\n" \
                    "A=M\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M+1"

    return return_string.replace("//varName", varName)


def stack_push_constant(index):
    return_string = "@"+index+"\n" \
                    "D=A\n" \
                    "@SP\n" \
                    "A=M\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M+1"

    return return_string

def stack_push_temp_or_pointer(location, i):
    """receives string - a name of the location in memory which can be one of the following:
    argument, local, this, that, pointer, temp. and i a string representation pf the relative location from
    'location' argument"""
    if location == "temp":
        location = "5"
    else:
        location = "3"

    return_string = "@//location\n" \
                    "D=A\n" \
                    "@//i\n" \
                    "A=D+A\n" \
                    "D=M\n" \
                    "@SP\n" \
                    "A=M\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M+1"
    return_string = return_string.replace("//location", location)
    return_string = return_string.replace("//i", i)
    return return_string



def stack_push(location, i):
    if location == "static":
        return stack_push_static(i)

    elif location == "constant":
        return stack_push_constant(i)

    elif location == "temp" or location == "pointer":
        return stack_push_temp_or_pointer(location, i)

    else:
        return stack_push_rest(location, i)



def stack_pop(location, i):
    if location == "static":
        return stack_pop_staic(i)

    elif location == "temp" or location == "pointer":
        return stack_pop_temp_or_pointer(location, i)
    else:
        return stack_pop_rest(location, i)



def stack_pop_staic(i):
    varName = build_static_var_name(i)

    return_string = "@SP\n" \
                    "M=M-1\n" \
                    "A=M\n" \
                    "D=M\n" \
                    "@//varName\n" \
                    "M=D"

    return return_string.replace("//varName", varName)



def stack_pop_rest(location, i):
    return_string = "@//location\n" \
                    "D=M\n" \
                    "@//i\n" \
                    "D=D+A\n" \
                    "@13\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M-1\n" \
                    "A=M\n" \
                    "D=M\n" \
                    "@13\n" \
                    "A=M\n" \
                    "M=D"

    location = determine_location(location)
    return_string = return_string.replace("//location", location)
    return_string = return_string.replace("//i", i)
    return return_string


def stack_pop_temp_or_pointer(location, i):
    if location == "temp":
        location = "5"
    else:
        location = "3"

    return_string = "@//location\n" \
                    "D=A\n" \
                    "@//i\n" \
                    "D=D+A\n" \
                    "@13\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M-1\n" \
                    "A=M\n" \
                    "D=M\n" \
                    "@13\n" \
                    "A=M\n" \
                    "M=D"

    return_string = return_string.replace("//location", location)
    return_string = return_string.replace("//i", i)
    return return_string



def determine_location(location):
    if location == "local":
        location = "LCL"

    elif location == "argument":
        location = "ARG"

    elif location == "this":
        location = "THIS"

    elif location == "that":
        location = "THAT"

    return location


def build_static_var_name(i):
    return g_filename + "." + i


def asm_add():
    add_command = "@SP //Start of an ADD command\n" \
                  "M=M-1\n" \
                  "A=M\n" \
                  "D=M //D holds the value of Y\n" \
                  "A=A-1\n" \
                  "M=M+D"
    return add_command


def asm_sub():
    sub_command = "@SP //Start of a SUB command\n" \
                  "M=M-1\n" \
                  "A=M\n" \
                  "D=M //D holds the value of Y\n" \
                  "A=A-1\n" \
                  "M=M-D"
    return sub_command


def asm_eq():
    global eq_calls
    eq_command = "@SP //Start of a eq command\n" \
                 "M=M-1\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "A=A-1\n" \
                 "D=M-D\n" \
                 "@EQ_EQUALS"+str(eq_calls)+"\n" \
                 "D;JEQ\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "M=0\n" \
                 "@EQ_END"+str(eq_calls)+"\n" \
                 "0;JMP\n" \
                 "(EQ_EQUALS"+str(eq_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "M=-1\n" \
                 "(EQ_END"+str(eq_calls)+")"
    eq_calls += 1
    return eq_command



def asm_gt():
    global gt_calls
    gt_command = "@SP\n" \
                 "M=M-1\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "@Y_IS_NEG" + str(gt_calls)+"\n" \
                 "D;JLT\n" \
                 "//here if y>=0\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "D=M\n" \
                 "@FALSE" + str(gt_calls)+"\n" \
                 "D;JLT\n" \
                 "//here iff x,y>=0\n" \
                 "@SP\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "A=A-1\n" \
                 "D=M-D\n" \
                 "@TRUE" + str(gt_calls)+ "\n" \
                 "D;JGT"+" //x,y>=0, x-y>0\n" \
                 "@FALSE" + str(gt_calls) + "\n" \
                 "0;JMP //x,y>=0, x-y<=0\n" \
                 "(Y_IS_NEG"+str(gt_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "D=M //D holds value of x\n" \
                 "@X_IS_NEG"+str(gt_calls)+"\n" \
                 "D;JLT\n" \
                 "@TRUE"+str(gt_calls)+" //here iff y<0, x>=0\n" \
                 "0;JMP\n" \
                 "(X_IS_NEG"+str(gt_calls)+") //here iff x,y<0\n" \
                 "@SP\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "A=A-1\n" \
                 "D=D-M //D holds the value of y-x\n" \
                 "@TRUE"+str(gt_calls)+"\n" \
                 "D;JLT //here iff x,y<0, y-x>=0\n" \
                 "@FALSE"+str(gt_calls)+"\n" \
                 "0;JMP\n" \
                 "(TRUE"+str(gt_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "M=-1\n" \
                 "@END"+str(gt_calls)+"\n" \
                 "0;JMP\n" \
                 "(FALSE"+str(gt_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "M=0\n" \
                 "(END"+str(gt_calls)+")"

    gt_calls += 1
    return gt_command



def asm_lt():
    global lt_calls

    lt_command = "@SP\n" \
                 "M=M-1\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "@Y_LT_NEG" + str(lt_calls)+"\n" \
                 "D;JLT\n" \
                 "//here if y>=0\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "D=M\n" \
                 "@LT_TRUE" + str(lt_calls)+"\n" \
                 "D;JLT\n" \
                 "//here iff x,y>=0\n" \
                 "@SP\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "A=A-1\n" \
                 "D=D-M\n" \
                 "@LT_TRUE" + str(lt_calls)+ "\n" \
                 "D;JGT"+" //x,y>=0, x-y>0\n" \
                 "@LT_FALSE" + str(lt_calls) + "\n" \
                 "0;JMP //x,y>=0, x-y<=0\n" \
                 "(Y_LT_NEG"+str(lt_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "D=M //D holds value of x\n" \
                 "@X_LT_NEG"+str(lt_calls)+"\n" \
                 "D;JLT\n" \
                 "@LT_FALSE"+str(lt_calls)+" //here iff y<0, x>=0\n" \
                 "0;JMP\n" \
                 "(X_LT_NEG"+str(lt_calls)+") //here iff x,y<0\n" \
                 "@SP\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "A=A-1\n" \
                 "D=M-D //D holds the value of y-x\n" \
                 "@LT_TRUE"+str(lt_calls)+"\n" \
                 "D;JLT //here iff x,y<0, y-x>=0\n" \
                 "@LT_FALSE"+str(lt_calls)+"\n" \
                 "0;JMP\n" \
                 "(LT_TRUE"+str(lt_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "M=-1\n" \
                 "@LT_END"+str(lt_calls)+"\n" \
                 "0;JMP\n" \
                 "(LT_FALSE"+str(lt_calls)+")\n" \
                 "@SP\n" \
                 "A=M-1\n" \
                 "M=0\n" \
                 "(LT_END"+str(lt_calls)+")"

    lt_calls += 1
    return lt_command



def asm_and():
    and_command = "@SP //Start of an AND command\n" \
                  "M=M-1\n" \
                  "A=M\n" \
                  "D=M\n" \
                  "A=A-1\n" \
                  "M=D&M"
    return and_command


def asm_or():
    or_command = "@SP //Start of an OR command\n" \
                 "M=M-1\n" \
                 "A=M\n" \
                 "D=M\n" \
                 "A=A-1\n" \
                 "M=D|M"
    return or_command



def asm_not():
    not_command = "@SP //Start of an NOT command\n" \
                  "A=M-1\n" \
                  "M=!M"
    return not_command



def translate_arithmetic_logic_cmd(command_type):
    # print(command_type)
    if command_type == "add":
        return asm_add()
    elif command_type == "sub":
        return asm_sub()
    elif command_type == "neg":
        return "@SP // Start of NEG command\n" \
               "A=M-1\n" \
               "D=0\n" \
               "M=D-M"
    elif command_type == "eq":
        return asm_eq()
    elif command_type == "gt":
        return asm_gt()
    elif command_type == "lt":
        return asm_lt()
    elif command_type == "and":
        return asm_and()
    elif command_type == "or":
        return asm_or()
    elif command_type == "not":
        return asm_not()
    else:
        return "an unrecognized command"


def get_flow_label(label):
    return "("+g_current_func+label+")"


def get_flow_goto(location):
    goto_string = "@"+g_current_func+location+"\n0;JMP"
    return goto_string

def get_goto(location):
    goto_string = "@"+location+"\n0;JMP"
    return goto_string

def get_flow_ifgoto(location):
    if_goto = "@SP\n" \
              "M=M-1\n" \
              "A=M\n" \
              "D=M\n" \
              "@"+g_current_func+location+"\n" \
              "D;JGT\n" \
              "D;JLT"
    return if_goto


def translate_flow_cmd(command_parts):
    if command_parts[0] == "label":
        return get_flow_label(command_parts[1])
    elif command_parts[0] == "goto":
        return get_flow_goto(command_parts[1])
    elif command_parts[0] == "if-goto":
        return get_flow_ifgoto(command_parts[1])


def asm_func_declaration(funcName, nVars):
    """
    :param funcName: the name of the function
    :param i: the number of local arguments the function has
    :return: an assembly string representing the function declaration
    """
    global g_current_func
    g_current_func = funcName+"$"
    return_string = "(" + funcName + ")\n" \
                    "@0\n" \
                    "D=A\n"
    for i in range(int(nVars)):
        return_string += "@SP\n" \
                        "A=M\n" \
                        "M=D\n" \
                        "@SP\n" \
                        "M=M+1\n"\

    return return_string


def asm_func_call(funcName, nArgs):
    global func_calls

    Pointers = ["LCL", "ARG", "THIS", "THAT"]
    return_address = funcName+"_call"+str(func_calls)   # making a globally unique func name

    return_string = asm_push_label_value(return_address)+"\n"   # using the label that is declared later for return add

    for i in range(len(Pointers)):
        Recovery_string = "@//Pointer\n" \
                          "D=M\n" \
                          "@SP\n" \
                          "A=M\n" \
                          "M=D\n" \
                          "@SP\n" \
                          "M=M+1\n"
        return_string += Recovery_string.replace("//Pointer", Pointers[i])


    # reposition ARG, ARG = SP-5-nArgs
    return_string += "@SP\n" \
                     "D=M\n" \
                     "@5\n" \
                     "D=D-A\n" \
                     "@" + str(nArgs) + "\n" \
                     "D=D-A\n" \
                     "@ARG\n" \
                     "M=D\n"

    # repositioning LCL, LCL = SP
    return_string += "@SP\n" \
                     "D=M\n" \
                     "@LCL\n" \
                     "M=D\n"

    # transfer control to the called function
    return_string += get_goto(funcName)+"\n"

    #declare a label for the return function
    return_string += "("+return_address+")"

    func_calls += 1

    return return_string


def asm_push_label_value(label_name):
    """
    :param label_name: a string representing the label name
    :return: assembly code that pushes the the address of the variable @label_name into the stack
    """
    return_string = "@"+label_name+"\n" \
                    "D=A\n" \
                    "@SP\n" \
                    "A=M\n" \
                    "M=D\n" \
                    "@SP\n" \
                    "M=M+1"
    return return_string


def asm_return():
    global Recovery_Pointers
    return_string = "@LCL\n" \
                    "D=M\n" \
                    "@endFrame\n" \
                    "M=D\n" \
                    "@5\n" \
                    "A=D-A\n" \
                    "D=M\n" \
                    "@retAddr\n" \
                    "M=D\n"
    #*ARG = pop()
    return_string += "@ARG\n" \
                     "D=M\n" \
                     "@13\n" \
                     "M=D\n" \
                     "@SP\n" \
                     "A=M-1\n" \
                     "D=M\n" \
                     "@13\n" \
                     "A=M\n" \
                     "M=D\n"

    #SP = ARG+1
    return_string += "@ARG\n" \
                     "D=M+1\n" \
                     "@SP\n" \
                     "M=D\n"

    # Recovering calling function initial pointers state, THAT, THIS, ARG and LCL
    recovery_string = "@endFrame\n" \
                      "M=M-1\n" \
                      "A=M\n" \
                      "D=M\n" \
                      "@//recovery_pointer\n" \
                      "M=D\n"

    for i in range(len(Recovery_Pointers)):
        return_string += recovery_string.replace("//recovery_pointer", Recovery_Pointers[i])

    #
    return_string += "@retAddr\n" \
                     "A=M\n" \
                     "0;JMP\n" \
                     "// function END"
    return return_string


def translate_function_cmds(command_parts):
    # input is an array. the first argument will be "function", "call" or "return"
    # second argument will be the name of the function
    # third argument will be the number of arguments / local variables (depends)
    if command_parts[0] == "function":
        return asm_func_declaration(command_parts[1], command_parts[2])
    elif command_parts[0] == "call":
        return asm_func_call(command_parts[1], command_parts[2])
    else:  # return statement
        return asm_return()


def write_cmd(asm_file, command):
    """
    This function writes a translated vm command as an assembly command into
    the supplied .asm file. The function uses helper functions to translate
    code according to the type of command being processed.
    :param asm_file: a .asm file (destination for assembly code)
    :param command: a command to translate and write into asm_file
    :return: None.
    """
    command_parts = command.split(" ")
    command_type = command_parts[0]
    if command_type == "push" or command_type == "pop":
        segment = command_parts[1]
        index = command_parts[2]
        if command_type == "push":
            asm_command = stack_push(segment, index)
        else:
            asm_command = stack_pop(segment, index)
    elif command_type == "add" or command_type == "sub" or \
                    command_type == "neg" or command_type == "eq" or \
                    command_type == "lt" or command_type == "gt" or \
                    command_type == "and" or command_type == "or" or \
                    command_type == "not":
        asm_command = translate_arithmetic_logic_cmd(command_type)
    elif command_type == "label" or command_type == "goto" or \
                    command_type == "if-goto":
        asm_command = translate_flow_cmd(command_parts)
    else:
        asm_command = translate_function_cmds(command_parts)
    asm_file.write(asm_command+"\n")


def get_commands(vm_file):
    """
    This function process an assembly file before it's translation to machine
    code. It creates a dictionary, and places into it all markers in the code,
    and assigns each one of them it's location in code, allowing to use it as
    a reference in future. While doing so, it deletes each marker's
    declaration.
    The function also clears all whitespaces and comments from the code.
    Any line which is not a comment, empty, or a marker declaration is
    inserted to a list of ordered commands, later used for creating a hack
    machine code binary.
    :param assembly_file: an .asm file
    :return: the created dictionary and commands list.
    """
    commands_list = list()
    for command in vm_file.readlines():
        command = command.split("//")[0]  # getting rid of comments
        command = " ".join(command.split())  # getting rid of whitespaces
        if command:
            commands_list.append(command)
    return commands_list


def translate_file(vm_file_name, asm_file):
    """
    A function that receives a name of a .vm and an .asm files.
    The function will create the specified .asm file respective to
    the supplied virtual machine code, line by line, using helper functions.
    :param vm_file_name: a name of a .vm file to translate to assembly.
    :param asm_file_name: a name of a source file to write assembly code to.
    :return: None
    """
    vm_file = open(vm_file_name)
    command_list = get_commands(vm_file)
    for command in command_list:
        write_cmd(asm_file, command)


def build_bootstrap_code():
    bootstrap_code = "@256\n" \
                     "D=A\n" \
                     "@SP\n" \
                     "M=D\n"

    bootstrap_code += asm_func_call("Sys.init", "0") + "\n"
    return bootstrap_code


def translate_files():
    """
    This function works on supplied arguments by the user. The arguments are
    either an .vm file or a directory. If given a directory, the function
    will operate on each of the .vm files contained within it, if any exist.
    The file(s) name(s) will be sent to....
    :return: None.
    """
    path = os.path.expanduser(sys.argv[1])
    global g_filename

    bootstrap_code = build_bootstrap_code()
    if os.path.isdir(path):
        asm_file_name = path + "/" + str(path.split("/")[-1]) + ".asm"
        # folder_name = path.split("\\")
        #print(asm_file_name)
        asm_file = open(asm_file_name, 'w')
        #asm_file.write(bootstrap_code)
        file_root = path + "/"
        for file in os.listdir(path):
            filename = os.path.splitext(file)
            if filename[1] == ".vm":
                g_filename = filename[0].split("/")[-1]
                #print(g_filename)
                translate_file(file_root + file, asm_file)
    else:

        filename = os.path.splitext(path)
        g_filename = filename[0].split("/")[-1]
        asm_file_name = filename[0] + ".asm"
        asm_file = open(asm_file_name, 'w')
        #asm_file.write(bootstrap_code)
        translate_file(path, asm_file)


translate_files()
