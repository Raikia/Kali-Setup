#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing git", 1)
        apt_install('git')
        print_status("Configuring global author", 1)
        run_command('git config --global user.name {0}'.format(escape(config.get('git', 'name', fallback="Anonymous"))))
        run_command('git config --global user.email {0}'.format(escape(config.get('git', 'email', fallback="anonymous@domain.com"))))

        print_status("Setting some defaults", 1)
        run_command('git config --global core.editor "vim"')
        run_command('git config --global merge.tool vimdiff')
        run_command('git config --global merge.conflictstyle diff3')
        run_command('git config --global mergetool.prompt false')
        run_command('git config --global push.default simple')
        