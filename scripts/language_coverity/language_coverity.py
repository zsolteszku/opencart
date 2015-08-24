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

def check_files(reference_filepath, check_filepath):
    global key_errors
    global total_reference_keys
    global total_check_keys
    global interactive
    with open(reference_filepath, "r") as reference_file, open(check_filepath, "r") as check_file:
        reference_keys = get_keys(reference_file)
        check_keys = get_keys(check_file)
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


def main():
    parser = ExtendedArgumentParser(description="LanguageCoverity for OpenCart")
    parser.add_argument("-c", "--check_lang_path", required=True, type="DIR", help="Path to the lang to check: e.x.: <path_to_opencart>/upload/catalog/language/hungarian")
    parser.add_argument("-r", "--reference_lang_path", type="DIR", help="Path to the reference lang: e.x.: <path_to_opencart>/upload/catalog/language/english")
    parser.add_argument("-o", "--output_file", default="output.txt", type=argparse.FileType('w'), help="OutputFile")
    parser.add_argument("-e", "--error_file", default="error.txt", type=argparse.FileType('w'), help="ErrorFile")
    parser.add_argument("-i", "--interactive", action="store_true")
    parsed = parser.parse_args()
    global key_errors
    global file_errors
    global total_files
    global parsing_error
    global error_file
    global output_file
    global total_reference_keys
    global total_check_keys
    global interactive
    error_file = parsed.error_file
    output_file = parsed.output_file
    reference_path = os.path.abspath(parsed.reference_lang_path)
    check_path = os.path.abspath(parsed.check_lang_path)
    key_errors=0
    file_errors=0
    total_files=0
    parsing_error=0
    total_reference_keys=0
    total_check_keys=0
    interactive= parsed.interactive 
    for root, dirs, filenames in os.walk(reference_path):
        relroot = os.path.relpath(root, reference_path)
        for filename in filenames:
            total_files += 1
            logger.debug("root: {} filename: {}".format(relroot, filename))
            check_filepath = os.path.join(check_path, relroot, filename)
            if os.path.exists(check_filepath):
                check_files(os.path.join(root, filename), check_filepath)
            else:
                logger.error("Cannot find file but in the reference its exists: {}".format(check_filepath))
                file_errors += 1


    err("TotalReferenceKeys: {}\nTotalCheckKeys: {}\nTotalFiles: {}\nFileErrors: {}\nKeyErrors: {}\nParsingError: {}".format(total_reference_keys,total_check_keys,total_files, file_errors, key_errors, parsing_error))
           

if __name__ == "__main__":
    main()