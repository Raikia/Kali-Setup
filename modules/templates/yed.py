#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing yEd...unfortunately this isn't silent so really we're just downloading the installer to /opt/yed.sh", 1)
        yed_link = run_command_with_output('curl -s "https://www.yworks.com/downloads#yEd" | grep -Po \'filePath&quot;:&quot;([^&]+)&quot;\' | awk -F\\; \'{print $3}\' | awk -F\\& \'{print $1}\' | grep \'.sh\' | head -n 1', safe=True).strip()
        file_download("https://www.yworks.com{0}".format(yed_link), "/opt/yed.sh")
        run_command('chmod +x /opt/yed.sh')
        print_success("Done!", 1)