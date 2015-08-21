# -*- coding: utf-8 -*-
# Initially taken from:
# http://code.activestate.com/recipes/134892/
# Thanks to Danny Yoo
import sys
import os
import select
import tty
import termios


def readchar(wait_for_char=True):
    try:
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
    except:
        c = 1
    try:
        if wait_for_char or select.select([sys.stdin, ], [], [], 0.0)[0]:
            return os.read(sys.stdin.fileno(), 1)
    finally:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except:
            c = 2
    return None
