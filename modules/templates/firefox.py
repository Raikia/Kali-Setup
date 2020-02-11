#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing Firefox", 1)
        apt_install(['firefox-esr', 'unzip'])
        print_warning('Firefox will spawn for 30 seconds to go through the "first run" process', 2)
        run_command("sleep 2")
        run_command("timeout 25 firefox-esr", show_error=False)
        run_command("timeout 15 killall -9 -q -w firefox-esr", show_error=False)
        print_success("Done!", 1)

        