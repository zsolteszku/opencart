import argparse
import os
import sys
from os import access, W_OK


class ExtendedArgumentParser(argparse.ArgumentParser):
    default_subparser = None

    def __is_valid_directory(self, arg):
        if not os.path.isdir(arg):
            self.error('The directory {} does not exist!'.format(arg))
        elif not access(arg, os.W_OK):
            self.error('You do not have write permission to the directory {}!'.format(arg))
        else:
            # File exists so return the directory
            return arg

    def add_argument(self, *args, **kwargs):
        # Look for your FILE or DIR settings
        if 'type' in kwargs and kwargs['type'] is 'DIR':
            kwargs['type'] = lambda x: self.__is_valid_directory(x)
        super(ExtendedArgumentParser, self).add_argument(*args, **kwargs)

    def __set_default_subparser(self, name, args):
        """default subparser selection. Call after setup, just before parse_args()
		name: is the name of the subparser to call by default
		args: if set is the argument list handed to parse_args()

		, tested with 2.7, 3.2, 3.3, 3.4
		it works with 2.6 assuming argparse is installed
		"""
        subparser_found = False
        for arg in args:
            if arg in ['-h', '--help']:  # global help if no subparser
                break
        else:
            for x in self._subparsers._actions:
                if not isinstance(x, argparse._SubParsersAction):
                    continue
                for sp_name in x._name_parser_map.keys():
                    if sp_name in args:
                        subparser_found = True
            if not subparser_found:
                # insert default in first position, this implies no
                # global options without a sub_parsers specified
                args.insert(0, name)

    def set_default_subparser(self, name):
        self.default_subparser = name

    def parse_args(self, args=sys.argv[1:], namespace=None):
        if self.default_subparser is not None:
            self.__set_default_subparser(self.default_subparser, args)
        return super(ExtendedArgumentParser, self).parse_args(args, namespace)