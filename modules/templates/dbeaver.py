#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing dbeaver", 1)
        file_download('http://dbeaver.jkiss.org/files/dbeaver-ce_latest_amd64.deb', '{0}/dbeaver.deb'.format(get_home_folder()))
        run_command('dpkg -i {0}/dbeaver.deb'.format(get_home_folder()))
        run_command('ln -sf /usr/share/dbeaver/dbeaver /usr/local/bin/dbeaver')
        run_command('rm {0}/dbeaver.deb'.format(get_home_folder()))
        print_success("Done!", 1)