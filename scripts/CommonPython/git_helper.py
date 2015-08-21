__author__ = 'zsoltessig'

import os
import command

def find_git_folder():
    cwd = os.path.abspath("./")
    git_folder = cwd
    while not os.path.exists(os.path.join(git_folder, ".git")):
        dir = os.path.dirname(git_folder)
        if os.path.abspath(dir) == os.path.abspath(git_folder):
            raise Exception("Do not found git folder! Tried to get from %s".format(git_folder))
        git_folder = dir
    return git_folder


def find_branch():
    return command.execute("git rev-parse --abbrev-ref HEAD")

def find_feature_id():
    branch_name = find_branch()
    feature_str = "feature/";
    pos = branch_name.index(feature_str) + len(feature_str)
    return branch_name[pos:-1]

def reset_all_files():
    command.execute("git reset HEAD")

def status_porcelain():
    return command.execute("git status --porcelain")

from enum import Enum

Status = Enum(["DELETED", "ADDED", "MODIFIED", "RENAMED"])

from colorama import Fore

def status_to_color(status):
    if status == Status.DELETED:
        return Fore.RED
    elif status == Status.ADDED:
        return Fore.MAGENTA
    else:
        return Fore.GREEN

def necessary_tabs(status):
    if status == Status.MODIFIED:
        return ""
    else:
        return "\t"

class FileStaus:

    def __init__(self, fileName, status):
        self.file_name = fileName
        self.status = status

    def colored(self):
        return status_to_color(self.status) + self.__str__() + Fore.RESET

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{}\t{}".format(self.status + necessary_tabs(self.status), self.file_name)


class RenamedFile(FileStaus):
    to_file = None

    def __init__(self, fileName, toFile):
        FileStaus.__init__(self, fileName, Status.RENAMED)
        self.to_file = toFile

    def __str__(self):
        return "{}\t{} \t->\t {}".format(self.status, self.file_name, self.to_file)


def get_file_statuses():
    out = status_porcelain()
    statuses = []
    for line in out.split(os.linesep):
        if line.startswith("R  ") or line.startswith("RM "):
            stripped_line = line[2:].strip()
            strip_str = "->"
            index = stripped_line.index(strip_str)
            from_file = stripped_line[:index].strip()
            to_file = stripped_line[index+len(strip_str):].strip()
            statuses.append(RenamedFile(from_file, to_file))
        elif line.startswith("M  ") or line.startswith(" M "):
            file_name = line[2:].strip()
            statuses.append(FileStaus(file_name, Status.MODIFIED))
        elif line.startswith("D  ") or line.startswith(" D "):
            file_name = line[2:].strip()
            statuses.append(FileStaus(file_name, Status.DELETED))
        elif line.startswith("??") or line.startswith("A  ") or line.startswith("AM "):
            file_name = line[2:].strip()
            statuses.append(FileStaus(file_name, Status.ADDED))
        elif line.strip() != "":
            raise Exception("Dont know the status for: {}".format(line))

    return statuses

def get_renamed_pairs():
    out = status_porcelain()
    pairs = []
    for line in out.split(os.linesep):
        if line.startswith("R  ") or line.startswith("RM "):
            stripped_line = line[1:].strip()
            strip_str = "->"
            index = stripped_line.index(strip_str)
            from_file = stripped_line[:index].strip()
            to_file = stripped_line[index+len(strip_str):].strip()
            pairs.append((from_file, to_file))
    return pairs

def add(files_ws):
    cmd = ["git", "add"]
    for file_ws in files_ws:
        cmd.append(file_ws.file_name)
        if(file_ws.status == Status.RENAMED):
            cmd.append(file_ws.to_file)
    out = command.execute(cmd)
    print(out)

def commit(message):
    print(command.execute(["git", "commit", "-m", message]))

def diff(files):
    cmd = ["git", "diff", "--color"]
    for file in files:
        cmd.append(file)
    print(command.execute(cmd))