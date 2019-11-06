#!/usr/bin/env python3

import sys
import os
import subprocess
from modules.common.printer import print_success,print_error
from modules.common import config
from modules.common import installer

def main():
    config_file_location = None
    if len(sys.argv) == 2:
        if sys.argv[1] == '-g':
            conf = config.Config(None)
            conf.generate_config('setup_config.ini')
            print_success("Configuration file generated: ./setup_config.ini")
            sys.exit(0)
        else:
            config_file_location = sys.argv[1]
    conf = config.Config(config_file_location)
    conf.load_config()
    install = installer.Installer(conf)
    install.run()






if __name__ == '__main__':
    main()