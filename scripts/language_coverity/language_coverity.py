import os
# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')
common_python_path_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CommonPython")
sys.path.append(common_python_path_dir)

from ArgHelper import ExtendedArgumentParser
import argparse
import install_package
from install_package import PackageInfo
import codecs

install_package.install_if_necessary(
    PackageInfo("setuptools", "https://pypi.python.org/packages/source/s/setuptools/setuptools-15.1.tar.gz"))
install_package.install_if_necessary(
    PackageInfo("colorama", "https://pypi.python.org/packages/source/c/colorama/colorama-0.3.3.tar.gz"))
install_package.install_if_necessary(
    PackageInfo("colorlog", "https://pypi.python.org/packages/source/c/colorlog/colorlog-2.6.0.tar.gz"))

import logging
from colorlog import ColoredFormatter
from colorama import init, AnsiToWin32

init(wrap=False)
stream = AnsiToWin32(sys.stdout).stream

logger = logging.getLogger("language_coverity")
logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(stream)
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
import re
pattern = re.compile(ur'\$_\[[\'"](.*)[\'"]\]\s*=\s*[\'"](.*)[\'"];')
print_duplicate = False

def err(msg):
    logger.error(msg)
    error_file.write(msg+"\n")

def get_keys(file):
    global parsing_error
    result = dict()
    linenum = 0
    for line in file.readlines():
        linenum += 1
        line = str(line).strip()
        if line.startswith("$"):
            matches = re.match(pattern, line)
            if matches is None:
                parsing_error += 1
                err("Parsing error at: {}:{} in line: {}".format(file.name, linenum, line))
            else:
                key = matches.group(1)
                value = matches.group(2)
                result[key]=value
    return result

class LanguageValue:

    def __init__(self, key, file, value ):
        self.key = key
        self.file = file
        self.value = value

def add_to_all_dictionary(all_dic, dic):
    for key in dic:
        value = dic[key]
        if key in all_dic:
            if value != all_dic[key]:
                err("Found duplicate key, but value is different. Key = \"{}\" Value1 = \"{}\" Value2 = \"{}\"".format(key, value, all_dic[key]))
        else:
            all_dic[key] = value

def parse_file_pair(reference_filepath, check_filepath, add_to_all):
    global key_errors, interactive, total_reference_keys, total_check_keys, all_reference_keys, all_check_keys
    with codecs.open(reference_filepath, "r", "utf-8") as reference_file, codecs.open(check_filepath, "r", "utf-8") as check_file:
        reference_keys = get_keys(reference_file)
        check_keys = get_keys(check_file)
        if add_to_all:
            add_to_all_dictionary(all_reference_keys, reference_keys)
            add_to_all_dictionary(all_check_keys, check_keys)
            return
    total_reference_keys+=len(reference_keys)
    total_check_keys +=len(check_keys)
    if interactive:
        check_file = codecs.open(check_filepath, "a", "utf-8")
    firstError = True
    for key in reference_keys:
        if not key in check_keys:
            if interactive:
                sys.stdout.write("{} ({})> Key for ['{}'](English is: \"{}\"): ".format(check_file.name,sys.getdefaultencoding(), key, reference_keys[key]))
                good = sys.stdin.readline().strip().decode(sys.stdin.encoding).encode("utf8")
                if firstError:
                    check_file.write(u"\n\n<?php\n//Missing keys with language_coverity script")
                    firstError = False
                check_file.write(u"\n$_['{}']        = '{}';".format(key, good))
            else:
                key_errors += 1
                err("Key error. Not found key: {} in file: {}".format(key, check_file.name))
    if interactive:
        if not firstError:
            check_file.write("\n?>")
        check_file.close()

def parse_files(add_to_all):
    if add_to_all:
        print("Parsing all lang files...")
    global reference_path, check_path, total_files, file_errors, reference_lang, check_lang
    for root, dirs, filenames in os.walk(reference_path):
        relroot = os.path.relpath(root, reference_path)
        for filename in filenames:
            total_files += 1
            logger.debug("root: {} filename: {}".format(relroot, filename))
            if filename == "{}.php".format(reference_lang):
                check_filename = "{}.php".format(check_lang)
            else:
                check_filename = filename
            check_filepath = os.path.abspath(os.path.join(check_path, relroot, check_filename))
            if os.path.exists(check_filepath):
                parse_file_pair(os.path.join(root, filename), check_filepath, add_to_all)
            else:
                logger.error("Cannot find file but in the reference its exists: {}".format(check_filepath))
                file_errors += 1

def main():
    parser = ExtendedArgumentParser(description="LanguageCoverity for OpenCart")
    parser.add_argument("-p", "--path_to_langs", required=True, type="DIR", help="Path to the languages directory")
    parser.add_argument("-c", "--check_lang", required=True, help="Check lang")
    parser.add_argument("-r", "--reference_lang", help="Reference lang")
    parser.add_argument("-e", "--error_file", default="error.txt", type=argparse.FileType('w'), help="ErrorFile")
    parser.add_argument("-i", "--interactive", action="store_true")
    parsed = parser.parse_args()
    global key_errors, file_errors, total_files, parsing_error, error_file, total_reference_keys, total_check_keys, interactive
    global reference_lang, check_lang, reference_path, check_path
    global all_reference_keys, all_check_keys
    all_reference_keys = dict()
    all_check_keys = dict()
    error_file = parsed.error_file
    reference_lang = parsed.reference_lang
    check_lang = parsed.check_lang
    reference_path = os.path.abspath(os.path.join(parsed.path_to_langs, reference_lang))
    check_path = os.path.abspath(os.path.join(parsed.path_to_langs, check_lang))
    if not os.path.isdir(reference_path) or not os.path.isdir(check_path):
        raise Exception("Cannot find {} or {} lang in path {}".format(reference_lang, check_lang, parsed.path_to_langs))
    key_errors=0
    file_errors=0
    total_files=0
    parsing_error=0
    total_reference_keys=0
    total_check_keys=0
    interactive = parsed.interactive
    parse_files(False)
    err("TotalReferenceKeys: {}\nTotalCheckKeys: {}\nTotalFiles: {}\nFileErrors: {}\nKeyErrors: {}\nParsingError: {}".format(total_reference_keys,total_check_keys,total_files, file_errors, key_errors, parsing_error))
           

if __name__ == "__main__":
    main()