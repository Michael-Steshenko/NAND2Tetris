import sys
import os


""" CONSTANTS """
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

""" Global variables"""
# A global variable representing the number of variables created in the
# supplied assembly code. When translating multiple files, this variable is
# set to 0 at the beginning of each translation process.
numOfVariables = 0


def translate_c_command(command):
    command_array = command.split("=")
    if len(command_array) == 1:  # no destination
        command_and_jump_array = command_array[0].split(";")
        destination_command = ""
    else:  # if length = 2
        destination_command = command_array[0]
        command_and_jump_array = command_array[1].split(";")
    if len(command_and_jump_array) == 1:  # no jump
        jump_command = ""
        compute_command = command_and_jump_array[0]
    else:  # if length = 2
        compute_command = command_and_jump_array[0]
        jump_command = command_and_jump_array[1]
    compute_bin = compute_command_to_bin(compute_command)
    destination_bin = destination_command_to_bin(destination_command)
    jump_bin = jump_command_to_bin(jump_command)
    return compute_bin+destination_bin+jump_bin


def compute_command_to_bin(compute_command):
    if "*" in compute_command:
        return mul_command_to_bin(compute_command)

    elif ">>" in compute_command or "<<" in compute_command:
        return shift_command_to_bin(compute_command)

    elif "M" in compute_command:
        return m_command_to_bin(compute_command)

    else:
        return a_command_to_bin(compute_command)


def mul_command_to_bin(compute_command):
    if compute_command == "D*A":
        return "1000000000"
    elif compute_command == "D*M":
        return "1001000000"


def shift_command_to_bin(compute_command):
    if compute_command == "D<<":
        return "1010110000"
    elif compute_command == "A<<":
        return "1010100000"
    elif compute_command == "M<<":
        return "1011100000"
    elif compute_command == "D>>":
        return "1010010000"
    elif compute_command == "A>>":
        return "1010000000"
    elif compute_command == "M>>":
        return "1011000000"


def m_command_to_bin(compute_command):
    prefix = "1111"
    # replacing the M in the M command to an A,
    # this way we can use the A command func
    compute_command = compute_command.replace("M", "A")
    return a_command_to_bin(compute_command, prefix)


def a_command_to_bin(compute_command, prefix="1110"):
    # shared A and M commands
    if compute_command == "A":
        suffix = "110000"
    elif compute_command == "!A":
        suffix = "110001"
    elif compute_command == "-A":
        suffix = "110011"
    elif compute_command == "A+1":
        suffix = "110111"
    elif compute_command == "A-1":
        suffix = "110010"
    elif compute_command == "D+A":
        suffix = "000010"
    elif compute_command == "D-A":
        suffix = "010011"
    elif compute_command == "A-D":
        suffix = "000111"
    elif compute_command == "D&A":
        suffix = "000000"
    elif compute_command == "D|A":
        suffix = "010101"

    # A only commands
    elif compute_command == "0":
        suffix = "101010"
    elif compute_command == "1":
        suffix = "111111"
    elif compute_command == "-1":
        suffix = "111010"
    elif compute_command == "D":
        suffix = "001100"
    elif compute_command == "!D":
        suffix = "001101"
    elif compute_command == "-D":
        suffix = "001111"
    elif compute_command == "D+1":
        suffix = "011111"
    elif compute_command == "D-1":
        suffix = "001110"

    return prefix+suffix


def destination_command_to_bin(destination_command):
    left_bit, middle_bit, right_bit = "0", "0", "0"
    if "M" in destination_command:
        right_bit = "1"
    if "D" in destination_command:
        middle_bit = "1"
    if "A" in destination_command:
        left_bit = "1"
    return left_bit + middle_bit + right_bit


def jump_command_to_bin(jump_command):
    left_bit, middle_bit, right_bit = "0", "0", "0"
    if jump_command == "JMP":
        return "111"
    if jump_command == "JNE":
        return "101"
    if "G" in jump_command:
        right_bit = "1"
    if "E" in jump_command:
        middle_bit = "1"
    if "L" in jump_command:
        left_bit = "1"
    return left_bit + middle_bit + right_bit


def translate_to_binary(command):
    """
    A function that translates a number into binary, and formatting it to fit
    the machine code language word length (16 bit)
    :param command: an integer to transform into hack binary
    :return: hack binary code
    """
    int_command = int(command)
    binary_command = bin(int_command)[2:]
    missing_bits = CMD_LEN - len(binary_command)
    cmd_prefix = missing_bits * str(0)
    binary_command = str(cmd_prefix) + str(binary_command)
    return binary_command + "\n"


def translate_a_command(marker_dictionary, cmd):
    """
    A function that gets a assembly command and translated it into machine
    code, using a supplied marker dictionary.
    This function is designed to update the supplied marker dictionary.
    :param marker_dictionary: a dictionary of pointers
    :param cmd: an assembly command line
    :return: the machine code binary respective to the supplied assembly line
    """
    if cmd.isdigit():
        return translate_to_binary(cmd)
    else:
        if cmd in marker_dictionary:
            return translate_to_binary(marker_dictionary[cmd])
        else:
            global numOfVariables
            marker_dictionary[cmd] = VAR_FIRST_MEM + numOfVariables
            numOfVariables += 1
            return translate_to_binary(VAR_FIRST_MEM + numOfVariables - 1)


def write_cmd(hack_file, marker_dictionary, cmd):
    """
    This function writes a translated assembly name as hack machine code into
    the supplied .hack file. The function uses helper functions to translate
    code according to the type of code.
    :param hack_file: a .hack file (destination for hack machine code)
    :param marker_dictionary: a dictionary of pointers
    :param cmd: a command to translate and write into hack_file
    :return: None.
    """
    if cmd[0] == '@':
        hack_file.write(translate_a_command(marker_dictionary, cmd[1:]))
    else:
        hack_file.write(translate_c_command(cmd) + "\n")


def load_constants():
    """
    A function that creates a dictionary containing all the hack assembly
    constants and their respective binary values, including I/O and reserved
    RAM locations
    :return: the created dictionary
    """
    marker_dictionary = dict()
    marker_dictionary["SP"] = SP
    marker_dictionary["LCL"] = LCL
    marker_dictionary["ARG"] = ARG
    marker_dictionary["THIS"] = THIS
    marker_dictionary["THAT"] = THAT
    marker_dictionary["SCREEN"] = SCREEN
    marker_dictionary["KBD"] = KBD
    for i in range(0, RAM_RESERVE_END):
        marker_dictionary["R"+str(i)] = i
    return marker_dictionary


def pre_process_asm_file(assembly_file):
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
    line_counter = 0
    marker_dictionary = load_constants()
    commands_list = list()
    for command in assembly_file.readlines():
        command = command.split("/")[0]  # getting rid of comments
        command = "".join(command.split())  # getting rid of whitespaces
        if command:
            if command.startswith('('):
                marker_dictionary[command[1:-1]] = line_counter
                continue
            commands_list.append(command)
            line_counter += 1
    return commands_list, marker_dictionary


def assemble_file(assembly_file_name, hack_file_name):
    """
    A function that receives names of an .asm file and a .hack file.
    The function will create the specified .hack file, and using helper
    functions will write to it hack machine code, line by line, respective to
    the supplied assembly code.
    :param assembly_file_name: a name of an .asm file to translate to machine.
    :param hack_file_name: a name of a source file to write machine code to.
    :return: None
    """
    global numOfVariables
    numOfVariables = 0
    assembly_file = open(assembly_file_name)
    command_list, marker_dictionary = pre_process_asm_file(assembly_file)
    hack_file = open(hack_file_name, 'w')
    for command in command_list:
        write_cmd(hack_file, marker_dictionary, command)
    # print(marker_dictionary) - useful for troubleshooting and understanding


def assemble_files():
    """
    This function works on supplied arguments by the user. The arguments are
    either an .asm file or a directory. If given a directory, the function
    will operate on each of the .asm files contained within it, if any exist.
    The file(s) name(s) will be sent to assemble_file func, which in turn,
    and by helper functions, will translate (each) .asm file to a respective
    .hack file - a hack computer binary file.
    When a folder is supplied, all .hack files will be stored in that folder.
    :return: None.
    """
    path = os.path.expanduser(sys.argv[1])
    if os.path.isdir(path):
        file_root = path + "/"
        for file in os.listdir(path):
            filename = os.path.splitext(file)
            if filename[1] == ".asm":
                hack_file_name = file_root + filename[0] + ".hack"
                assemble_file(file_root + file, hack_file_name)
    else:
        filename = os.path.splitext(path)
        hack_file_name = filename[0] + ".hack"
        assemble_file(path, hack_file_name)


assemble_files()
