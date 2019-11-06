#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing dbeaver", 1)
        file_download('http://dbeaver.jkiss.org/files/dbeaver-ce_latest_amd64.deb', '/root/dbeaver.deb')
        run_command('dpkg -i /root/dbeaver.deb')
        run_command('ln -sf /usr/share/dbeaver/dbeaver /usr/local/bin/dbeaver')
        run_command('rm /root/dbeaver.deb')
        print_success("Done!", 1)