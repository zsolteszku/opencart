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
             PackageInfo("colorlog", "https://pypi.python.org/packages/source/c/colorlog/colorlog-2.6.0.tar.gz"),
             PackageInfo("six", "https://pypi.python.org/packages/source/s/six/six-1.9.0.tar.gz#md5=476881ef4012262dfc8adc645ee786c4"),
             PackageInfo("oauth2client", "https://pypi.python.org/packages/source/o/oauth2client/oauth2client-1.4.12.tar.gz#md5=829a05a559b43215d67947aaff9c11b5"),
             PackageInfo("httplib2", "https://pypi.python.org/packages/source/h/httplib2/httplib2-0.9.1.tar.gz#md5=c49590437e4c5729505d034cd34a8528"),
             PackageInfo("uritempalte", "https://pypi.python.org/packages/source/u/uritemplate/uritemplate-0.6.tar.gz#md5=ecfc1ea8d62c7f2b47aad625afae6173"),
             PackageInfo("apiclient", "https://pypi.python.org/packages/source/g/google-api-python-client/google-api-python-client-1.4.1.tar.gz")])

from apiclient.http import BatchHttpRequest

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

    def get_defaults(self, google_translate):
        if not google_translate:
            return ("There are value(s) for key(\"{}\") that already defined, you can select one of them:\n\t0. Create new value\n".format(self.key),1)
        else:
            return ("There are value(s) for key(\"{}\") that already defined, you can select one of them:\n\t0. Create new value\n\t1. Google Translate: {}\n".format(self.key, google_translate),2)

    def get_prompt(self, google_translate = None):
        str, idx = self.get_defaults(google_translate)
        for entity in self.values:
            str += "\t{}. {}\n".format(idx, entity)
            idx += 1
        return str + "Select a number: "

    def get_good(self, index, google_translate = None):
        if index <= len(self.values) + (1 if google_translate else 0):
            if index == 0:
                return get_new_key("Please give me the new value: ")
            elif index == 1 and google_translate is not None:
                #google_translate
                return google_translate
            else:
                return self.values[index- (2 if google_translate else 1) ].value
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
            check_file.write(u"//Processed with language_coverity script")
            for key in file_error.check_keys:
                write_pair(check_file, key, check_keys[key])
            try:
                for lang_error in file_error.lang_errors:
                    key = lang_error.key
                    reference_value = lang_error.reference_value
                    good = None
                    if key in all_check_keys:
                        while good is None:
                            sys.stdout.write("{} > {}".format(check_file.name, all_check_keys[key].get_prompt()))
                            response = sys.stdin.readline().strip()
                            if response.isdigit():
                                good = all_check_keys[key].get_good(int(response), lang_error.google_translate)
                            if good is None:
                                err("Wrong response got. Please select a number between 0 and {}!".format(len(all_check_keys[key].values)))
                    else:
                        good = get_new_key("{} > Key for ['{}'](English is: \"{}\"): ".format(check_file.name, key, reference_value))
                    write_pair(check_file, key, good)
            except:
                check_file.write(u"\n?>\n")
                check_file.close()
                raise

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

def fetch_google_translate():
     print("Fetching google translates...")


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
    key_errors = dict()
    file_errors=0
    total_files=0
    parsing_error=0
    total_reference_keys=0
    total_check_keys=0
    interactive = parsed.interactive
    parse_files()
    if interactive:
        fetch_google_translate()
        fix_errors()
    key_errors_size = calcualte_key_errors()
    wr("TotalReferenceKeys: {}\nTotalCheckKeys: {}\nTotalFiles: {}\nFileErrors: {}\nKeyErrors: {}\nParsingError: {}".format(total_reference_keys,total_check_keys,total_files, file_errors, key_errors_size, parsing_error))
           

if __name__ == "__main__":
    main()