#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing vim", 1)
        apt_install('vim')
        print_status("Configuring vim with some defaults", 1)
        file_append_or_replace('/etc/vim/vimrc', '.*syntax on', 'syntax on')
        file_append_or_replace('/etc/vim/vimrc', '.*set background=dark', 'set background=dark')
        file_append_or_replace('/etc/vim/vimrc', '.*set showcmd', 'set showcmd')
        file_append_or_replace('/etc/vim/vimrc', '.*set showmatch', 'set showmatch')
        file_append_or_replace('/etc/vim/vimrc', '.*set ignorecase', 'set ignorecase')
        file_append_or_replace('/etc/vim/vimrc', '.*set smartcase', 'set smartcase')
        file_append_or_replace('/etc/vim/vimrc', '.*set incsearch', 'set incsearch')
        file_append_or_replace('/etc/vim/vimrc', '.*set autowrite', 'set autowrite')
        file_append_or_replace('/etc/vim/vimrc', '.*set hidden', 'set hidden')
        file_append_or_replace('/etc/vim/vimrc', '.*set mouse=.*', 'set mouse=')
        file_append_or_replace('/etc/vim/vimrc', '.*set number.*', 'set number')
        file_append_or_replace('/etc/vim/vimrc', '.*set expandtab.*', 'set expandtab')
        file_append_or_replace('/etc/vim/vimrc', '.*set smarttab.*', 'set smarttab')
        file_append_or_replace('/etc/vim/vimrc', '.*set softtabstop.*', 'set softtabstop=4')
        file_append_or_replace('/etc/vim/vimrc', '.*set shiftwidth.*', 'set shiftwidth=4')
        file_append_or_replace('/etc/vim/vimrc', '.*set foldmethod=marker.*', 'set foldmethod=marker')
        file_append_or_replace('/etc/vim/vimrc', '.*nnoremap <space> za.*', 'nnoremap <space> za')
        file_append_or_replace('/etc/vim/vimrc', '.*set hlsearch.*', 'set hlsearch')
        file_append_or_replace('/etc/vim/vimrc', '.*set laststatus.*', 'set laststatus=2')
        file_append_or_replace('/etc/vim/vimrc', '.*set statusline.*', 'set statusline=%F%m%r%h%w\ (%{&ff}){%Y}\ [%l,%v][%p%%]')
        file_append_or_replace('/etc/vim/vimrc', '.*filetype on.*', 'filetype on')
        file_append_or_replace('/etc/vim/vimrc', '.*filetype plugin on.*', 'filetype plugin on')
        file_append_or_replace('/etc/vim/vimrc', '.*syntax.*', 'syntax enable')
        file_append_or_replace('/etc/vim/vimrc', '.*set grepprg.*', 'set grepprg=grep\ -nH\ $*')
        file_append_or_replace('/etc/vim/vimrc', '.*set wildmenu.*', 'set wildmenu')
        file_append_or_replace('/etc/vim/vimrc', '.*set wildmode.*', 'set wildmode=list:longest,full')
        file_append_or_replace('/etc/vim/vimrc', '.*set invnumber.*', ':nmap <F8> :set invnumber<CR>')
        file_append_or_replace('/etc/vim/vimrc', '.*set pastetoggle=<F9>.*', 'set pastetoggle=<F9>')
        file_append_or_replace('/etc/vim/vimrc', '.*:command Q q.*', ':command Q q')
        print_success("Done!", 1)
        