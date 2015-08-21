# -*- coding: utf-8 -*-
# This file is based on this gist:
# http://code.activestate.com/recipes/134892/
# So real authors are DannyYoo and company.
from __future__ import absolute_import
import sys

from . import key


if sys.platform.startswith('linux') or sys.platform.startswith("cygwin"):
    from readchar.readchar_linux import readchar
elif sys.platform == 'darwin':
    from readchar.readchar_linux import readchar
elif sys.platform.startswith('win32'):
    from readchar.readchar_windows import readchar
else:
    raise NotImplemented('The platform %s is not supported yet' % sys.platform)


def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    buffer = getchar(True)

    while True:
        if buffer not in key.ESCAPE_SEQUENCES:
            return buffer
        c = getchar(False)
        if c is None:
            return buffer
        buffer += c
    return buffer
