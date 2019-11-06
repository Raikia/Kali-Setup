#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing ntp", 1)
        apt_install(['ntp', 'ntpdate'])
        run_command('ntpdate -b -s -u pool.ntp.org')
        run_command('systemctl restart ntp')
        run_command('systemctl disable ntp')
        print_status("Done!", 1)
        