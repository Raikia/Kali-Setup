#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing zsh", 1)
        apt_install('zsh')
        print_success("Done!", 1)

        print_status("Installing oh-my-zsh", 1)
        run_command('curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh | zsh')
        file_append_once('{0}/.zshrc'.format(get_home_folder()), 'setopt interactivecomments', 'interactivecomments')
        file_append_once('{0}/.zshrc'.format(get_home_folder()), 'setopt ignoreeof', 'ignoreeof')
        file_append_once('{0}/.zshrc'.format(get_home_folder()), 'setopt correctall', 'correctall')
        file_append_once('{0}/.zshrc'.format(get_home_folder()), 'setopt globdots', 'globdots')
        file_append_once('{0}/.zshrc'.format(get_home_folder()), 'source $HOME/.aliases', '.aliases')
        if config.getboolean('general', '4k', fallback=False):
            file_append_once('{0}/.zshrc'.format(get_home_folder()), 'export GDK_SCALE=2')
        file_replace('{0}/.zshrc'.format(get_home_folder()), 'ZSH_THEME=.*', 'ZSH_THEME="mh"')
        file_replace('{0}/.zshrc'.format(get_home_folder()), 'plugins=.*', 'plugins=(git-extras tmux dirhistory python pip)')
        file_append_once('{0}/.zshrc'.format(get_home_folder()), 'source $HOME/.xinitrc')
        
        print_success("Done!", 1)