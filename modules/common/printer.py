#!/usr/bin/env python3

import sys


_PRINTER_GREEN = '\033[32m'
_PRINTER_YELLOW = '\033[93m'
_PRINTER_RED = '\033[31m'
_PRINTER_WHITE = '\033[37m'
_PRINTER_RESET = '\033[0m'


def get_input(msg, default=None, valid_inputs=None):
    try:
        while True:
            user_input = input('  {0} {1}:\n > '.format(msg, '[{0}]'.format(default) if default is not None else '')).strip()
            if user_input == '' and default is not None:
                return default
            elif valid_inputs is None or user_input.lower() in valid_inputs:
                return user_input
            else:
                print_error('Invalid input! {}\n'.format(('Expecting: ' + ', '.join(valid_inputs)) if valid_inputs is not None else ''))
    except KeyboardInterrupt:
        print()
        print()
        print_error("CTRL+C detected!  Quitting!")
        sys.exit(1)

def print_success(msg, indent=0):
    print(" "*(indent*4) + _PRINTER_GREEN + " [+] " + _PRINTER_RESET + msg)

def print_warning(msg, indent=0):
    print(" "*(indent*4) + _PRINTER_YELLOW + " [!] " + _PRINTER_RESET + msg)

def print_error(msg, indent=0):
    print(" "*(indent*4) + _PRINTER_RED + " [-] Error: " + msg + _PRINTER_RESET)

def print_status(msg, indent=0):
    print(" "*(indent*4) + _PRINTER_WHITE + " [~] " + _PRINTER_RESET + msg)

