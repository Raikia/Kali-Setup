#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Configuring bash", 1)
        file_backup('/etc/bash.bashrc')
        file_append_once('/etc/bash.bashrc', 'shopt -sq cdspell', 'cdspell')
        file_append_once('/etc/bash.bashrc', 'shopt -s autocd', 'autocd')
        file_append_once('/etc/bash.bashrc', 'shopt -sq checkwinsize', 'checkwinsize')
        file_append_once('/etc/bash.bashrc', 'shopt -sq nocaseglob', 'nocaseglob')
        file_append_once('/etc/bash.bashrc', 'HISTSIZE=10000', 'HISTSIZE')
        file_append_once('/etc/bash.bashrc', 'HISTFILESIZE=10000', 'HISTFILESIZE')
        if config.getboolean('general', '4k', fallback=False):
            file_append_once('/etc/bash.bashrc', 'export GDK_SCALE=2')
        print_success("Done", 1)
        