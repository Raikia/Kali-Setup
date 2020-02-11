#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing git", 1)
        apt_install('git')
        print_status("Configuring global author", 1)
        run_command('git config --global user.name {0}'.format(escape(config.get('git', 'name', fallback="Anonymous"))), as_user=True)
        run_command('git config --global user.email {0}'.format(escape(config.get('git', 'email', fallback="anonymous@domain.com"))), as_user=True)

        print_status("Setting some defaults", 1)
        run_command('git config --global core.editor "vim"', as_user=True)
        run_command('git config --global merge.tool vimdiff', as_user=True)
        run_command('git config --global merge.conflictstyle diff3', as_user=True)
        run_command('git config --global mergetool.prompt false', as_user=True)
        run_command('git config --global push.default simple', as_user=True)
        