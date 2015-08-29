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

install_package.install_packages([ PackageInfo("setuptools", "https://pypi.python.org/packages/source/s/setuptools/setuptools-15.1.tar.gz"),
             PackageInfo("colorama", "https://pypi.python.org/packages/source/c/colorama/colorama-0.3.3.tar.gz"),
             PackageInfo("colorlog", "https://pypi.python.org/packages/source/c/colorlog/colorlog-2.6.0.tar.gz")])

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
ignored_keys = ["heading_title", "text_edit", "text_empty", "text_success", "text_message"]
google_translate_file_suffix = "_google_translate.txt"

def err(msg):
    logger.error(msg)
    error_file.write(msg+"\n")

def wr(msg):
    print(msg)
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
                err("{}:{} >Parsing error in line: {}".format(file.name, linenum, line))
            else:
                key = matches.group(1).decode("utf-8").encode(sys.stdout.encoding, "ignore")
                value = matches.group(2).decode("utf-8").encode(sys.stdout.encoding, "ignore")
                if not value:
                    err("{}:{} > Value is null or empty for key: {}".format(file.name, linenum, key))
                elif key in result and result[key] != value:
                    err("{}:{}> Duplicate key('{}', Value1='{}' Value2='{}')".format(file.name, linenum, key, result[key], value))
                else:
                    result[key]=value
    return result

class LanguageEntity:

    def __init__(self, file, value):
        self.file = file
        self.value = value

    def __str__(self):
        return "{}> \"{}\"".format(self.file, self.value)

class LanguageValue:

    def __init__(self, key, file, value ):
        self.key = key
        self.values = [LanguageEntity(file, value)]

    def add_value(self, file, value):
        self.values.append(LanguageEntity(file, value))

    def get_defaults(self, lang_error):
        if not lang_error.google_translate:
            return ("There are value(s) for key(\"{}\") that already defined, you can select one of them(Current english is \"{}\"):\n\t0. Create new value\n".format(self.key, lang_error.reference_value),1)
        else:
            return ("There are value(s) for key(\"{}\") that already defined, you can select one of them(Current english is \"{}\"):\n\t0. Create new value\n\t1. Google Translate: {}\n".format(self.key, lang_error.reference_value, lang_error.google_translate),2)

    def get_prompt(self, lang_error):
        str, idx = self.get_defaults(lang_error)
        for entity in self.values:
            str += "\t{}. {}\n".format(idx, entity)
            idx += 1
        return str + "Select a number: "

    def get_len(self, lang_error):
        return len(self.values) + (1 if lang_error.google_translate else 0)

    def get_good(self, index, lang_error):
        if index <= self.get_len(lang_error):
            if index == 0:
                return get_new_key("Please give me the new value: ")
            elif index == 1 and lang_error.google_translate is not None:
                #google_translate
                return lang_error.google_translate
            else:
                return self.values[index- (2 if lang_error.google_translate else 1) ].value
        return None

    def contains(self, value):
        for entity in self.values:
            if entity.value == value:
                return True
        return False

    def values_str(self):
        str = "["
        for entity in self.values:
            str += entity.value + ", "
        return str[:-2] + "]" 

class LanguageError:

    def __init__(self, check_filename, reference_filename, key, reference_value):
        self.check_filename = check_filename
        self.reference_filename = reference_filename
        self.key = key
        self.reference_value = reference_value
        self.google_translate = None

    def set_google_translate(self, google_translate):
        self.google_translate = google_translate

class FileError:

    def __init__(self, check_keys, lang_errors):
        self.check_keys = check_keys
        self.lang_errors = lang_errors

def add_to_all_dictionary(all_dic, dic, file):
    for key in dic:
        if key in ignored_keys:
            continue
        value = dic[key]
        if key in all_dic:
            if not all_dic[key].contains(value):
                all_dic[key].add_value(file, value)
                #logger.warning("Duplicate key, but value is not the same: {} Values: {}".format(key, all_dic[key].values_str()))
        else:
            all_dic[key] = LanguageValue(key, file, value)

def write_pair(check_file, key, good):
    check_file.write(u"\n$_['{}']\t\t\t= '{}';".format(key.decode(sys.stdin.encoding), good.decode(sys.stdin.encoding).encode("utf8")))

def get_new_key(msg):
    sys.stdout.write(msg)
    return sys.stdin.readline().strip()

def fix_errors():
    global key_errors, all_check_keys
    for check_filepath in key_errors:
        with codecs.open(check_filepath, "w", "utf-8") as check_file:
            file_error = key_errors[check_filepath]
            check_file.seek(0)
            check_file.write(u"<? php\n//Processed with language_coverity script")
            for key in file_error.check_keys:
                write_pair(check_file, key, file_error.check_keys[key])
            try:
                for lang_error in file_error.lang_errors:
                    key = lang_error.key
                    reference_value = lang_error.reference_value
                    good = None
                    if key in all_check_keys:
                        while good is None:
                            sys.stdout.write("{} > {}".format(check_file.name, all_check_keys[key].get_prompt(lang_error)))
                            response = sys.stdin.readline().strip()
                            if response.isdigit():
                                good = all_check_keys[key].get_good(int(response), lang_error)
                            if good is None:
                                err("Wrong response got. Please select a number between 0 and {}!".format(all_check_keys[key].get_len(lang_error)))
                    else:
                        if lang_error.google_translate is None:
                            good = get_new_key("{} > Key for ['{}'](English is: \"{}\"): ".format(check_file.name, key, reference_value))
                        else:
                            good = get_new_key("{} > Key for ['{}'](English is: \"{}\")! Press enter to use google translate (\"{}\"): ".format(check_file.name, key, reference_value, lang_error.google_translate))
                            if not good or good.isspace():
                                good = lang_error.google_translate
                    if good == "EXIT":
                        raise Exception("pressed exit")
                    elif good == "SKIP":
                        continue
                    write_pair(check_file, key, good)
            finally:
                check_file.write(u"\n?>\n")
                check_file.close()

def parse_file_pair(reference_filepath, check_filepath):
    global key_errors, total_reference_keys, total_check_keys, all_reference_keys, all_check_keys
    with codecs.open(reference_filepath, "r", "utf-8") as reference_file, codecs.open(check_filepath, "r", "utf-8") as check_file:
        reference_keys = get_keys(reference_file)
        check_keys = get_keys(check_file)
        add_to_all_dictionary(all_reference_keys, reference_keys, reference_filepath)
        add_to_all_dictionary(all_check_keys, check_keys, check_filepath)
    total_reference_keys+=len(reference_keys)
    total_check_keys +=len(check_keys)
    for key in reference_keys:
        if not key in check_keys:
            lang_error = LanguageError(check_filepath, reference_filepath, key, reference_keys[key])
            if not check_filepath in key_errors:
                key_errors[check_filepath] = FileError(check_keys, [lang_error])
            else:
                key_errors[check_filepath].lang_errors.append(lang_error)
    

def parse_files():
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
            if not os.path.exists(check_filepath):
                logger.error("Cannot find file but in the reference its exists: {}. Will create it!".format(check_filepath))
                file_errors += 1
                if not os.path.exists(os.path.dirname(check_filepath)):
                    logger.error("Cannot find dir but in the reference its exists: {}. Will create it!".format(os.path.dirname(check_filepath)))
                    os.makedirs(os.path.dirname(check_filepath))
                codecs.open(check_filepath, "a", "utf-8").close()
            parse_file_pair(os.path.join(root, filename), check_filepath)
                
def calcualte_key_errors():
     global key_errors
     key_errors_size = 0
     for file in key_errors:
         key_errors_size += len(key_errors[file].lang_errors)
     return key_errors_size    

def calcualte_key_errors_characters():
     global key_errors
     characters = 0
     for file in key_errors:
         for error in key_errors[file].lang_errors:
             characters += len(error.reference_value)
     return characters   
 
def write_output():
     global key_errors, output_file
     for file in key_errors:
        for error in key_errors[file].lang_errors:
            output_file.write("{}\n\n\n".format(error.reference_value).replace("\\'", "'").replace("\\\"", "\""))


def parse_google_translate_file(filename):
    result = []
    with codecs.open(filename, "r", "utf-8") as file:
            for line in file.read().splitlines():
                if line and not line.isspace():
                    result.append(line.decode("utf-8").encode(sys.stdout.encoding, "ignore"))
    return result

def fetch_google_translate():
    print("Fetching google translates...")
    global check_lang, reference_lang, google_translate_map, key_errors
    check_google_translate = check_lang + google_translate_file_suffix 
    reference_google_translate = reference_lang + google_translate_file_suffix
    if os.path.exists(check_google_translate) and os.path.exists(reference_google_translate):
        print("Found google translate so using it!")
        check_list = parse_google_translate_file(check_google_translate)
        ref_list = parse_google_translate_file(reference_google_translate)
        if len(check_list) == len(ref_list):
            for index in range(0, len(check_list)):
                google_translate_map[ref_list[index]] = check_list[index]
            print("GoogleTranslateMapSize = {}".format(len(google_translate_map)))
            print("Mapping...")
            for file in key_errors:
                for error in key_errors[file].lang_errors:
                    if error.reference_value in google_translate_map:
                        error.set_google_translate(google_translate_map[error.reference_value])
        else:    
            err("Invalid google translate files! Reason: Size is not equal. {} size is {}. {} size is {}".format(check_google_translate, len(check_list), reference_google_translate, len(ref_list)))
    else:
        err("Not found google translate files: {} and {}".format(check_google_translate, reference_google_translate))


def main():
    parser = ExtendedArgumentParser(description="LanguageCoverity for OpenCart")
    parser.add_argument("-p", "--path_to_langs", required=True, type="DIR", help="Path to the languages directory")
    parser.add_argument("-c", "--check_lang", required=True, help="Check lang")
    parser.add_argument("-r", "--reference_lang", help="Reference lang")
    parser.add_argument("-e", "--error_file", default="error.txt", type=argparse.FileType('w'), help="ErrorFile")
    parser.add_argument("-o", "--output_file", default="output.txt", type=argparse.FileType("w"))
    parser.add_argument("-i", "--interactive", action="store_true")
    parsed = parser.parse_args()
    global key_errors, file_errors, total_files, parsing_error, error_file, total_reference_keys, total_check_keys, interactive
    global reference_lang, check_lang, reference_path, check_path
    global all_reference_keys, all_check_keys, output_file
    global google_translate_map
    google_translate_map = dict()
    all_reference_keys = dict()
    all_check_keys = dict()
    error_file = parsed.error_file
    output_file = parsed.output_file
    reference_lang = parsed.reference_lang
    check_lang = parsed.check_lang
    reference_path = os.path.abspath(os.path.join(parsed.path_to_langs, reference_lang))
    check_path = os.path.abspath(os.path.join(parsed.path_to_langs, check_lang))
    if not os.path.isdir(reference_path) or not os.path.isdir(check_path):
        raise Exception("Cannot find {} or {} lang in path {}".format(reference_lang, check_lang, parsed.path_to_langs))
    key_errors = dict()
    file_errors=0
    total_files=0
    parsing_error=0
    total_reference_keys=0
    total_check_keys=0
    interactive = parsed.interactive
    parse_files()
    write_output()
    if interactive:
        fetch_google_translate()
        fix_errors()
    key_errors_size = calcualte_key_errors()
    characters = calcualte_key_errors_characters()
    wr("TotalReferenceKeys: {}\nTotalCheckKeys: {}\nTotalFiles: {}\nFileErrors: {}\nKeyErrors: {}\nParsingError: {}\nTotal translated characters: {}".format(total_reference_keys,total_check_keys,total_files, file_errors, key_errors_size, parsing_error, characters))
           

if __name__ == "__main__":
    main()