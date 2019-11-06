#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing Ghidra", 1)
        ghidra_link = run_command_with_output('curl -s "https://ghidra-sre.org/" | grep \'Download Ghidra\' | cut -d\\" -f6', safe=True).strip()
        file_download("https://ghidra-sre.org/{0}".format(ghidra_link), "/opt/ghidra.zip")
        run_command('cd /opt/; unzip ghidra*.zip')
        run_command('rm /opt/ghidra*.zip')
        print_success("Done!", 1)