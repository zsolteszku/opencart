__author__ = 'zsoltessig'

import subprocess
import sys
import os

import readchar


class Command:
    def __init__(self, command_name, function_ptr):
        self.command_name = command_name
        self.function_ptr = function_ptr

    def __repr__(self):
        return self.command_name


# class Reprinter:
#     def __init__(self):
#         self.text = ''
#
#     def moveup(self, lines):
#         for _ in range(lines):
#             sys.stdout.write("\x1b[A")
#
#     def reprint(self, text):
#         # Clear previous text by overwritig non-spaces with spaces
#         self.moveup(self.text.count("\n"))
#         sys.stdout.write(re.sub(r"[^\s]", " ", self.text))
#
#         # Print new text
#         lines = min(self.text.count("\n"), text.count("\n"))
#         self.moveup(lines)
#         sys.stdout.write(text)
#         sys.stdout.flush()
#         self.text = text

class MyCmd:
    def __init__(self, commands):
        self.commands = commands
        self.reset()


    def reset(self):
        self.input = ""
        self.prefix = "> "
        self.aval_commands = []
        self.removed = False
        self.full_match = False

    def listen(self):
        self.reset()
        while(True):
            self.rewrite()
            c = readchar.readchar()
            if c == "\t":
                self.completition()
            elif c == "\b" or c == "\b \b" or c == u"\u007F":
                if self.input != "":
                    self.input = self.input[:-1]
                    self.removed = True
            elif c == "\n" or c == "\n\r":
                return self.done()
            else:
                self.input += c


    def completition(self):
        self.aval_commands = [x for x in self.commands if x.command_name.startswith(self.input)]
        if len(self.aval_commands) == 1:
            self.input = self.aval_commands[0].command_name
            self.full_match = True

    def rewrite(self):
        completitions = ""
        if not self.full_match:
            for cmds in self.aval_commands:
                if completitions != "":
                    completitions += "\t\t"
                completitions += cmds.command_name
        self.aval_commands = []
        if completitions != "":
            completitions = os.linesep + completitions + os.linesep
        else:
            completitions = "\r"
        print(completitions + self.prefix + self.input),
        if self.removed:
            print(" \b\b"),
        sys.stdout.flush()
        self.removed = False
        self.full_match = False

    def done(self):
        print(" ")
        return self.input


def execute(str):
   array = str if isinstance(str, list) else str.split()
   return subprocess.check_output(array)
    # out, err = p.communicate()
    # if err is not "":
    #     raise Exception("Get error message when trying to execute: \"{}\". Error is: \"{}\"".format(str, err))
    # return out


def ask(str):
    sys.stdout.write(str)
    return sys.stdin.readline().strip()

def ask_for_select_command(commands, default_command, logger):
    selected_command = None
    while selected_command is None:
        response = ask("\n\nPlease select a command: {}({}): ".format(commands, default_command))
        if response == "":
            response = default_command.command_name
        for cmd in commands:
            if response.strip() == cmd.command_name.strip():
                selected_command = cmd
        if selected_command is None:
            logger.error("Cannot find command named: {}. Please select from available commands!".format(response))
    return selected_command


def ask_for_select_command_with_tab_completition(commands, default_command, logger):
    selected_command = None
    cmdLine = MyCmd(commands)
    while selected_command is None:
        print("\n\nPlease select a command: {}({}): ".format(commands, default_command))
        response = cmdLine.listen()
        if response == "":
            response = default_command.command_name
        for cmd in commands:
            if response.strip() == cmd.command_name.strip():
                selected_command = cmd
        if selected_command is None:
            logger.error("Cannot find command named: {}. Please select from available commands!".format(response))
    return selected_command
