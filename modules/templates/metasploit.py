#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _CONFIG = """
load auto_add_route

load alias
alias del rm
alias handler use exploit/multi/handler

load sounds

setg TimestampOutput true
setg VERBOSE true

setg ExitOnSession false
setg EnableStageEncoding true
setg LHOST 0.0.0.0
setg LPORT 443
"""

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing metasploit", 1)
        apt_install('metasploit-framework')
        make_dir('/root/.msf4/modules/auxiliary')
        make_dir('/root/.msf4/modules/exploits')
        make_dir('/root/.msf4/modules/payloads')
        make_dir('/root/.msf4/modules/post')
        run_command('systemctl stop postgresql')
        run_command('systemctl start postgresql')
        run_command('msfdb reinit')
        run_command('sleep 5')
        file_write('/root/.msf4/msfconsole.rc', self._CONFIG)
        print_success("Done!", 1)

        print_status("Starting metasploit for the first time.", 1)
        run_command("msfdb start")
        run_command("msfconsole -q -x 'version;db_status;sleep 30;exit'")
        print_success("Done!", 1)
