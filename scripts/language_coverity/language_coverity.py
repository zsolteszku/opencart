import os
import sys
common_python_path_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CommonPython")
sys.path.append(common_python_path_dir)

from ArgHelper import ExtendedArgumentParser
import argparse
import install_package
from install_package import PackageInfo

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

logger = logging.getLogger("commit")
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


def main():
    parser = ExtendedArgumentParser(description="LanguageCoverity for OpenCart")
    parser.add_argument("-c", "--check_lang_path", required=True, type="DIR", help="Path to the lang to check: e.x.: <path_to_opencart>/upload/catalog/language/hungarian")
    parser.add_argument("-r", "--reference_lang_path", type="DIR", help="Path to the reference lang: e.x.: <path_to_opencart>/upload/catalog/language/english")
    parser.add_argument("-o", "--output_file", type=argparse.FileType('w'))

if __name__ == "__main__":
    main()