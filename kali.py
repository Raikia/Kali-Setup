#!/usr/bin/env python3

from colorama import Fore
import time
import os
import subprocess
import sys
import re


### SET THESE VARIABLES!
YOUR_NAME = "Raikia"
YOUR_EMAIL = "raikiasec@gmail.com"
TIMEZONE = 'America/Chicago'
HIDPI_MONITOR = True       # Set this True if you have a 4k monitor, False otherwise
COBALTSTRIKE_LICENSE = ''   # Leave blank if you don't have one
INSTALL_NEW_DE = True       # Set this to false if you want to stick with gnome
BLEEDING_EDGE_REPOS = True  # Set this to false if you dont want bleeding edge updates


### END VARIABLES

TOTAL_PARTS = -2
CURRENT_STAGE = 0
current_file = sys.argv[0] or 'kali.py'
with open(current_file, 'r') as content_file:
	for line in content_file:
		if 'do_action' in line:
			TOTAL_PARTS += 1


def main():
	show_header()
	check_environment()
	launch_configuration()
	show_ending()



def show_header():
	print("Starting Kali configuration script!")
	print("       By Chris King")
	print("")
	print(Fore.YELLOW + "This script expects a new Kali install from the normal ISO")
	print("It is not recommended running this on the non-default ISO" + Fore.RESET)
	print("")
	print(Fore.RED + "Pausing 10 seconds to make sure you want to continue. CTRL+C otherwise" + Fore.RESET)
	time.sleep(10)

def show_ending():
	print("")
	print("Completed setup!  Reboot!")

def check_environment():
	do_action("Checking if we are root")
	if os.geteuid() != 0:
		print_error("You must run this script as root!")
		sys.exit(1)
	else:
		print_success("We are root!")

def launch_configuration():
	global TOTAL_PARTS, CURRENT_STAGE, YOUR_NAME, YOUR_EMAIL, TIMEZONE, COBALTSTRIKE_LICENSE, BLEEDING_EDGE_REPOS

	## Set timezone
	do_action("Setting timezone")
	if TIMEZONE == '' or not file_exists('/usr/share/zoneinfo/{}'.format(TIMEZONE)):
		print_error("{0} is not a valid timezone... Cannot continue!".format(TIMEZONE))
		sys.exit(1)
	else:
		run_command('echo {0} > /etc/timezone'.format(TIMEZONE))
		run_command('ln -sf "/usr/share/zoneinfo/{0}" /etc/localtime'.format(TIMEZONE))
		run_command('dpkg-reconfigure -f noninteractive tzdata')
		print_success("Done")

	## Disable screensaver
	do_action("Disabling the screensaver")
	run_command("xset s 0 0")
	run_command("xset s off")
	file_append_once('/root/.xinitrc', "xset s off\n")
	# disable beep while we're at it
	file_append_once('/root/.xinitrc', "xset b off\n")
	run_command('gsettings set org.gnome.desktop.session idle-delay 0')
	print_success("Done")

	## Check internet
	do_action("Checking internet access")
	value = run_command("ping -c 1 -W 10 www.google.com")
	if value != 0:
		print_error("Uh oh, you don't have internet access! Fix that before continuing")
		sys.exit(1)
	else:
		print_success("Done")

	## Enable bleeding edge repos (if set)
	do_action("Enabling bleeding edge repositories")
	if BLEEDING_EDGE_REPOS:
		if not file_contains('/etc/apt/sources.list', 'kali-bleeding-edge'):
			run_command('echo "deb http://http.kali.org/kali kali-bleeding-edge contrib non-free main" >> /etc/apt/sources.list')
			print_success("Done")
		else:
			print_success("Already enabled!")
	else:
		print_success("Skipping...")

	## Update apt cache
	do_action("Updating repository cache")
	value = run_command('apt -qq update')
	if value != 0:
		print_error("Uh oh, the repositories broke!  Quitting...")
		sys.exit(1)
	else:
		print_success("Done")

	## Run system updates before installing stuff
	do_action("Running system updates")
	run_command("apt -y -qq clean")
	run_command("apt -y -qq autoremove")
	run_command('apt -y -qq update')
	run_command('export DEBIAN_FRONTEND=noninteractive; apt -qq update && APT_LISTCHANGES_FRONTEND=none apt -o Dpkg::Options::="--force-confnew" -y dist-upgrade --fix-missing', True, True)
	run_command("apt -y -qq clean")
	run_command("apt -y -qq autoremove")

	## Check if we are running as the latest kernel (may have just installed)
	do_action("Checking if we are running as the latest kernel")
	value = run_command_output('dpkg -l | grep linux-image- | grep -vc meta')
	if int(value) > 1:
		print_success("Detected {0} kernels".format(value.decode('ascii').rstrip("\n")))
		value = run_command("dpkg -l | grep linux-image | grep -v meta | sort -t '.' -k 2 -g | tail -n 1 | grep \"$(uname -r)\"")
		if value == 0:
			print_success("You are running the latest kernel!  All good")
		else:
			print_error("You are not running the latest kernel but its installed already!")
			print_error("Reboot and then re-run this script!")
			sys.exit(1)
	else:
		print_success("You are running the latest kernel!  All good")

	## Install kernel headers
	do_action("Installing the latest kernel headers")
	run_command("apt -y -qq install make gcc \"linux-headers-$(uname -r)\"", True)
	print_success("Done")


	## Install VM Tools
	do_action("Checking if we are running in a VM")
	in_vm = ""
	if run_command('dmidecode | grep -iq vmware') == 0:
		in_vm = "VMware"
	if run_command('dmidecode | grep -iq virtualbox') == 0:
		in_vm = "Virtualbox"
	print_success("Done")

	do_action("Installing VM Tools if running in a VM")
	if in_vm == "VMware":
		print_success("Running in VMware, installing tools...")
		run_command("apt -y -qq install open-vm-tools open-vm-tools-desktop", True)
		print_success("Done")
	elif in_vm == "Virtualbox":
		print_success("Running in Virtualbox, installing tools...")
		run_command("apt -y -qq install virtualbox-guest-x11", True)
		print_success("Done")
	else:
		print_success("Not in a VM")

	do_action("Writing mount shared folders script")
	if in_vm == "VMware":
		value = """#!/bin/bash
vmware-hgfsclient | while read folder; do
	echo "[i] Mounting ${folder}    (/mnt/hgfs/${folder})"
	mkdir -p "/mnt/hgfs/${folder}"
	umount -f "/mnt/hgfs/${folder}" 2>/dev/null
	vmhgfs-fuse -o allow_other -o auto_unmount ".host:/${folder}" "/mnt/hgfs/${folder}"
done

sleep 2s
"""
		file_write("/usr/local/sbin/mount-shared-folders", value)
		run_command("chmod +x /usr/local/sbin/mount-shared-folders")
		run_command("ln -sf '/usr/local/sbin/mount-shared-folders' '/root/Desktop/mount-shared-folders.sh'")
		print_success("Done")
	else:
		print_success("Not in VMware, so skipping")


	## Install NTP
	do_action("Installing ntp")
	run_command("apt -y -qq install ntp ntpdate", True)
	run_command("ntpdate -b -s -u pool.ntp.org")
	run_command("systemctl restart ntp")
	run_command("systemctl disable ntp")
	print_success("Done")


	## Install default kali tools
	do_action("Installing full kali meta package (might take a bit)")
	run_command("apt -y -qq install kali-linux-full", True)
	print_success("Done")

	## Set audio level
	do_action("Setting audio level")
	run_command("systemctl --user enable pulseaudio")
	run_command("systemctl --user start pulseaudio")
	run_command("pactl set-sink-mute 0 0")
	run_command("pactl set-sink-volume 0 25%")
	print_success("Done")

	## Set grub timeout
	value = 5
	if in_vm != "":
		value = 1
	do_action("Setting grub boot timeout to {0}".format(value))
	file_backup('/etc/default/grub')
	file_replace('/etc/default/grub', '^GRUB_TIMEOUT=.*', "GRUB_TIMEOUT={0}".format(value))
	file_replace('/etc/default/grub', '^GRUB_CMDLINE_LINUX_DEFAULT=.*', 'GRUB_CMDLINE_LINUX_DEFAULT="vga=0x0318"')
	run_command('update-grub', True, True)
	print_success("Done")


	## Configure login manager
	do_action("Configuring login manager")
	file_backup('/etc/gdm3/daemon.conf')
	file_replace('/etc/gdm3/daemon.conf', '^.*AutomaticLoginEnable = .*', 'AutomaticLoginEnable = true')
	file_replace('/etc/gdm3/daemon.conf', '^.*AutomaticLogin = .*', 'AutomaticLogin = root')
	print_success("Done")


	if INSTALL_NEW_DE:
		## Install xfce4
		do_action("Installing XFCE4")
		run_command('export DEBIAN_FRONTEND=noninteractive; apt -y -qq install curl xfce4 xfce4-mount-plugin xfce4-notifyd xfce4-places-plugin xfce4-power-manager', True, True)
		if in_vm == "":
			run_command('apt -y -qq install xfce4-battery-plugin')
		print_success("Done")


		## Configure xfce4	
		do_action("Configuring XFCE4")
		# This has so many actions I put it in its own function
		configure_xfce()
		print_success("Done")


	## Configure terminal
	do_action("Configuring the terminal")
	run_command('apt -y -qq install gconf2')
	run_command('gconftool-2 -s -t string /apps/gnome-terminal/profiles/Default/background_type solid')
	run_command('gconftool-2 -t bool -s /apps/gnome-terminal/profiles/Default/scrollback_unlimited true')
	run_command('gconftool-2 -t string -s /apps/gnome-terminal/profiles/Default/background_darkness 0.85611499999999996')
	print_success("Done")

	## Configure user home folders
	do_action("Configuring user home folders")
	run_command('find ~/ -maxdepth 1 -mindepth 1 -type d \( -name "Documents" -o -name "Music" -o -name "Pictures" -o -name "Public" -o -name "Templates" -o -name "Videos" \) -empty -delete')
	run_command('apt -y -qq install xdg-user-dirs')
	run_command('xdg-user-dirs-update')
	run_command('run -f /root/.cache/sessions/*')
	print_success("Done")

	## Configure bash
	do_action("Configuring bash")
	file_backup('/etc/bash.bashrc')
	file_append_once('/etc/bash.bashrc', 'shopt -sq cdspell', 'cdspell')
	file_append_once('/etc/bash.bashrc', 'shopt -s autocd', 'autocd')
	file_append_once('/etc/bash.bashrc', 'shopt -sq checkwinsize', 'checkwinsize')
	file_append_once('/etc/bash.bashrc', 'shopt -sq nocaseglob', 'nocaseglob')
	file_append_once('/etc/bash.bashrc', 'HISTSIZE=10000', 'HISTSIZE')
	file_append_once('/etc/bash.bashrc', 'HISTFILESIZE=10000', 'HISTFILESIZE')
	run_command("bash -c 'source /etc/bash.bashrc'", True, True)
	print_success("Done")


	## Configure global aliases
	do_action("Configuring global aliases")
	file_append_or_replace('/etc/bash.bashrc', '.*force_color_prompt=.*', 'force_color_prompt=yes')
	file_append_or_replace('/etc/bash.bashrc', "PS1='.*'", 'PS1=\'${debian_chroot:+($debian_chroot)}\\[\\033[01;31m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ \'')
	file_append_once('/etc/bash.bashrc', "export LS_OPTIONS='--color=auto'")
	file_append_once('/etc/bash.bashrc', 'eval "$(dircolors)"')
	file_append_once('/etc/bash.bashrc', "alias ls='ls $LS_OPTIONS'")
	file_append_once('/etc/bash.bashrc', "alias ll='ls $LS_OPTIONS -l'")
	file_append_once('/etc/bash.bashrc', "alias l='ls $LS_OPTIONS -lA'")
	file_replace('/etc/bash.bashrc', '#alias', 'alias')
	run_command("bash -c 'source /etc/bash.bashrc || source /root/.zshrc'")
	print_success("Done")

	## Install grc which provides colored command line output
	do_action("Installing grc")
	run_command('apt -y -qq install grc')
	print_success("Done")

	## Configure local aliases
	do_action("Configuring local aliases")
	grc_location = run_command_output('which grc').decode('ascii').rstrip()
	run_command('touch /root/.bash_aliases')
	file_append_once('/root/.bash_aliases', "## grc diff alias\nalias diff='{0} {1}'".format(grc_location, run_command_output('which diff').decode('ascii').rstrip()), 'grc diff')
	file_append_once('/root/.bash_aliases', "## grc dig alias\nalias dig='{0} {1}'\n".format(grc_location, run_command_output('which dig').decode('ascii').rstrip()), 'grc dig')
	file_append_once('/root/.bash_aliases', "## grc gcc alias\nalias gcc='{0} {1}'".format(grc_location, run_command_output('which gcc').decode('ascii').rstrip()), 'grc gcc')
	file_append_once('/root/.bash_aliases', "## grc ifconfig alias\nalias ifconfig='{0} {1}'".format(grc_location, run_command_output('which ifconfig').decode('ascii').rstrip()), 'grc ifconfig')
	file_append_once('/root/.bash_aliases', "## grc mount alias\nalias mount='{0} {1}'".format(grc_location, run_command_output('which mount').decode('ascii').rstrip()), 'grc mount')
	file_append_once('/root/.bash_aliases', "## grc netstat alias\nalias netstat='{0} {1}'".format(grc_location, run_command_output('which netstat').decode('ascii').rstrip()), 'grc netstat')
	file_append_once('/root/.bash_aliases', "## grc ping alias\nalias ping='{0} {1}'".format(grc_location, run_command_output('which ping').decode('ascii').rstrip()), 'grc ping')
	file_append_once('/root/.bash_aliases', "## grc ps alias\nalias ps='{0} {1}'".format(grc_location, run_command_output('which ps').decode('ascii').rstrip()), 'grc ps')
	file_append_once('/root/.bash_aliases', "## grc tail alias\nalias tail='{0} {1}'".format(grc_location, run_command_output('which tail').decode('ascii').rstrip()), 'grc tail')
	file_append_once('/root/.bash_aliases', "## grc traceroute alias\nalias traceroute='{0} {1}'".format(grc_location, run_command_output('which traceroute').decode('ascii').rstrip()), 'grc traceroute')
	file_replace('/root/.bashrc', '#alias', 'alias')
	file_replace('/root/.bash_aliases', '#alias', 'alias')
	contents = """
## grep aliases
alias grep="grep --color=auto"
alias ngrep="grep -n"

alias egrep="egrep --color=auto"

alias fgrep="fgrep --color=auto"

## tmux
alias tmux="tmux attach || tmux new"

## axel
alias axel="axel -a"

## screen
alias screen="screen -xRR"

## Checksums
alias sha1="openssl sha1"
alias md5="openssl md5"

## Force create folders
alias mkdir="/bin/mkdir -pv"

## List open ports
alias ports="netstat -tulanp"

## Get header
alias header="curl -I"

## Get external IP address
alias ipx="curl -s http://ipinfo.io/ip"

## DNS - External IP #1
alias dns1="dig +short @resolver1.opendns.com myip.opendns.com"

## DNS - External IP #2
alias dns2="dig +short @208.67.222.222 myip.opendns.com"

### DNS - Check ("#.abc" is Okay)
alias dns3="dig +short @208.67.220.220 which.opendns.com txt"

## Directory navigation aliases
alias ..="cd .."
alias ...="cd ../.."
alias ....="cd ../../.."
alias .....="cd ../../../.."


## Extract file, example. "ex package.tar.bz2"
ex() {
  if [[ -f $1 ]]; then
    case $1 in
      *.tar.bz2) tar xjf $1 ;;
      *.tar.gz)  tar xzf $1 ;;
      *.bz2)     bunzip2 $1 ;;
      *.rar)     rar x $1 ;;
      *.gz)      gunzip $1  ;;
      *.tar)     tar xf $1  ;;
      *.tbz2)    tar xjf $1 ;;
      *.tgz)     tar xzf $1 ;;
      *.zip)     unzip $1 ;;
      *.Z)       uncompress $1 ;;
      *.7z)      7z x $1 ;;
      *)         echo $1 cannot be extracted ;;
    esac
  else
    echo $1 is not a valid file
  fi
}
## strings
alias strings="strings -a"

## history
alias hg="history | grep"

### Network Services
alias listen="netstat -antp | grep LISTEN"

### HDD size
alias hogs="for i in G M K; do du -ah | grep [0-9]$i | sort -nr -k 1; done | head -n 11"

### Listing
alias ll="ls -l --block-size=1 --color=auto"

## nmap
alias nmap="nmap --reason --open --stats-every 3m --max-retries 1 --max-scan-delay 20 "

## aircrack-ng
alias aircrack-ng="aircrack-ng -z"

## airodump-ng 
alias airodump-ng="airodump-ng --manufacturer --wps --uptime"

## metasploit
alias msfc="systemctl start postgresql; msfdb start; msfconsole -q \"\$@\""
alias msfconsole="systemctl start postgresql; msfdb start; msfconsole \"\$@\""

## openvas
alias openvas="openvas-stop; openvas-start; sleep 3s; xdg-open https://127.0.0.1:9392/ >/dev/null 2>&1"

## mana-toolkit
alias mana-toolkit-start="a2ensite 000-mana-toolkit;a2dissite 000-default; systemctl restart apache2"
alias mana-toolkit-stop="a2dissite 000-mana-toolkit; a2ensite 000-default; systemctl restart apache2"

## ssh
alias ssh-start="systemctl restart ssh"
alias ssh-stop="systemctl stop ssh"

## samba
alias smb-start="systemctl restart smbd nmbd"
alias smb-stop="systemctl stop smbd nmbd"

## rdesktop
alias rdesktop="rdesktop -z -P -g 90% -r disk:local=\"/tmp/\""

## python http
alias http="python2 -m SimpleHTTPServer"

## www
alias wwwroot="cd /var/www/html/"
#alias www="cd /var/www/html/"

## ftp
alias ftproot="cd /var/ftp/"

## tftp
alias tftproot="cd /var/tftp/"

## smb
alias smb="cd /var/samba/"
#alias smbroot="cd /var/samba/"

## vmware
alias vmroot="cd /mnt/hgfs/"

## edb
alias edb="cd /usr/share/exploitdb/platforms/"
alias edbroot="cd /usr/share/exploitdb/platforms/"

## wordlist
alias wordlists="cd /usr/share/wordlists/"

## metasploit
alias msfconsole="systemctl start postgresql; msfdb start; msfconsole \"\$@\""

"""
	file_append('/root/.bash_aliases', contents)
	run_command("bash -c 'source /etc/bash.bashrc || source /root/.zshrc'")
	print_success("Done")

	## Install bash completion
	do_action("Installing bash completion")
	run_command('apt -y -qq install bash-completion')
	run_command("sed -i '/# enable bash completion in/,+7{/enable bash completion/!s/^#//}' '/etc/bash.bashrc'")
	print_success("Done")

	## Install zsh and oh-my-zsh
	do_action("Installing zsh and oh-my-zsh")
	run_command("apt -y -qq install zsh git curl")
	run_command('curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh | zsh')
	file_append_once('/root/.zshrc', 'setopt interactivecomments', 'interactivecomments')
	file_append_once('/root/.zshrc', 'setopt ignoreeof', 'ignoreeof')
	file_append_once('/root/.zshrc', 'setopt correctall', 'correctall')
	file_append_once('/root/.zshrc', 'setopt globdots', 'globdots')
	file_append_once('/root/.zshrc', 'source $HOME/.bash_aliases', '.bash_aliases')
	file_replace('/root/.zshrc', 'ZSH_THEME=.*', 'ZSH_THEME="mh"')
	file_replace('/root/.zshrc', 'plugins=.*', 'plugins=(git-extras tmux dirhistory python pip')
	file_append_once('/root/.zshrc', 'source $HOME/.xinitrc')
	# set zsh to default
	run_command('chsh -s "{0}"'.format(run_command_output('which zsh').decode('ascii').rstrip()))
	print_success("Done")

	## Install tmux
	do_action("Installing tmux")
	run_command("apt -y -qq install tmux")
	print_success("Done")

	## Install and configure vim
	do_action("Installing and configuring vim")
	run_command("apt -y -qq install vim")
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
	file_append_or_replace('/etc/vim/vimrc', '.*set expandtab.*', 'set expandtab\nset smarttab')
	file_append_or_replace('/etc/vim/vimrc', '.*set softtabstop.*', 'set softtabstop=4\nset shiftwidth=4')
	file_append_or_replace('/etc/vim/vimrc', '.*set foldmethod=marker.*', 'set foldmethod=marker')
	file_append_or_replace('/etc/vim/vimrc', '.*nnoremap <space> za.*', 'nnoremap <space> za')
	file_append_or_replace('/etc/vim/vimrc', '.*set hlsearch.*', 'set hlsearch')
	file_append_or_replace('/etc/vim/vimrc', '.*set laststatus.*', 'set laststatus=2\nset statusline=%F%m%r%h%w\ (%{&ff}){%Y}\ [%l,%v][%p%%]')
	file_append_or_replace('/etc/vim/vimrc', '.*filetype on.*', 'filetype on\nfiletype plugin on\nsyntax enable\nset grepprg=grep\ -nH\ $*')
	file_append_or_replace('/etc/vim/vimrc', '.*set wildmenu.*', 'set wildmenu\nset wildmode=list:longest,full')
	file_append_or_replace('/etc/vim/vimrc', '.*set invnumber.*', ':nmap <F8> :set invnumber<CR>')
	file_append_or_replace('/etc/vim/vimrc', '.*set pastetoggle=<F9>.*', 'set pastetoggle=<F9>')
	file_append_or_replace('/etc/vim/vimrc', '.*:command Q q.*', ':command Q q')
	file_append_once('/etc/bash.bashrc', 'export EDITOR="vim"')
	print_success("Done")

	## Install git
	do_action("Installing and configuring git")
	run_command('apt -y -qq install git')
	run_command('git config --global core.editor "vim"')
	run_command('git config --global merge.tool vimdiff')
	run_command('git config --global merge.conflictstyle diff3')
	run_command('git config --global mergetool.prompt false')
	run_command('git config --global push.default simple')
	run_command('git config --global user.name "{0}"'.format(YOUR_NAME))
	run_command('git config --global user.email "{0}"'.format(YOUR_EMAIL))
	print_success("Done")

	## Setup Firefox
	do_action("Installing and configuring firefox")
	run_command("apt -y -qq install unzip curl firefox-esr")
	print_success("Firefox will spawn for 30 seconds to go through the \"first run\" process")
	run_command("sleep 2")
	run_command("timeout 25 firefox")
	run_command("timeout 15 killall -9 -q -w firefox-esr")
	config_file = run_command_output("find ~/.mozilla/firefox/*.default*/ -maxdepth 1 -type f -name 'prefs.js' -print -quit").decode("ascii").rstrip()
	file_append_or_replace(config_file, '^.network.proxy.socks_remote_dns.*', 'user_pref("network.proxy.socks_remote_dns", true);')
	file_append_or_replace(config_file, '^.browser.safebrowsing.enabled.*', 'user_pref("browser.safebrowsing.enabled", false);')
	file_append_or_replace(config_file, '^.browser.safebrowsing.malware.enabled.*', 'user_pref("browser.safebrowsing.malware.enabled", false);')
	file_append_or_replace(config_file, '^.browser.safebrowsing.remoteLookups.enabled.*', 'user_pref("browser.safebrowsing.remoteLookups.enabled", false);')
	file_append_or_replace(config_file, '^.*browser.startup.page.*', 'user_pref("browser.startup.page", 0);')
	file_append_or_replace(config_file, '^.*privacy.donottrackheader.enabled.*', 'user_pref("privacy.donottrackheader.enabled", true);')
	file_append_or_replace(config_file, '^.*browser.showQuitWarning.*', 'user_pref("browser.showQuitWarning", true);')
	file_append_or_replace(config_file, '^.*extensions.https_everywhere._observatory.popup_shown.*', 'user_pref("extensions.https_everywhere._observatory.popup_shown", true);')
	file_append_or_replace(config_file, '^.network.security.ports.banned.override', 'user_pref("network.security.ports.banned.override", "1-65455");')
	run_command("mkdir -p /root/.config/xfce4/")
	file_append_or_replace('/root/.config/xfce4/helpers.rc', '^WebBrowser=.*', 'WebBrowser=firefox')
	print_success("Done")

	## Install firefox plugins
	do_action("Installing firefox plugins")
	plugin_folder = run_command_output("find ~/.mozilla/firefox/*.default*/ -maxdepth 0 -mindepth 0 -type d -name '*.default*' -print -quit").decode("ascii").rstrip() + "/extensions"
	if plugin_folder == "/extensions":
		print_error("Could not find firefox profile folder")
	else:
		run_command('mkdir -p {0}/'.format(plugin_folder))
		print_success("Downloading plugins")
		# SQLite Manager
		file_download("https://addons.mozilla.org/firefox/downloads/file/1024161/sqlite_manager-0.2.0-an+fx.xpi?src=search", "{0}/SQLiteManager@mrinalkant.blogspot.com.xpi".format(plugin_folder))
		# Cookies Manager+
		file_download("https://addons.mozilla.org/firefox/downloads/file/802399/cookie_manager-1.4-an+fx.xpi?src=search", "{0}/cookie-manager@robwu.nl.xpi".format(plugin_folder))
		# FoxyProxy Basic
		file_download("https://addons.mozilla.org/firefox/downloads/latest/15023/addon-15023-latest.xpi?src=dp-btn-primary", "{0}/foxyproxy-basic@eric.h.jung.xpi".format(plugin_folder))
		# User Agent Overrider
		file_download("https://addons.mozilla.org/firefox/downloads/file/969712/user_agent_switcher-0.2.4-an+fx.xpi?src=search", "{0}/useragentoverrider@qixinglu.com.xpi".format(plugin_folder))
		# Live HTTP Headers
		file_download("https://addons.mozilla.org/firefox/downloads/file/1044210/http_header_live-0.6.4-an+fx-linux.xpi?src=search", "{0}/{{ed102056-8b4f-43a9-99cd-6d1b25abe87e}}.xpi".format(plugin_folder))
		# HackBar
		file_download("https://addons.mozilla.org/firefox/downloads/file/1029136/hackbar-1.1.12-an+fx.xpi?src=search", "{0}/{{4c98c9c7-fc13-4622-b08a-a18923469c1c}}.xpi".format(plugin_folder))
		# uBlock
		file_download("https://addons.mozilla.org/firefox/downloads/file/1086463/ublock_origin-1.17.0-an+fx.xpi?src=search", "{0}/uBlock0@raymondhill.net.xpi".format(plugin_folder))

		## install plugins
		print_success("Installing the plugins")
		run_command('export ffpath="$(find ~/.mozilla/firefox/*.default*/ -maxdepth 0 -mindepth 0 -type d -name \'*.default*\' -print -quit)/extensions"; for FILE in $(find "${ffpath}" -maxdepth 1 -type f -name \'*.xpi\'); do d="$(basename "${FILE}" .xpi)"; mkdir -p "${ffpath}/${d}/"; unzip -q -o -d "${ffpath}/${d}/" "${FILE}";rm -f "${FILE}"; done', True, True) 
		run_command('timeout 15 firefox')
		run_command('timeout 5 killall -9 -q -w firefox-esr')
		run_command('sleep 3')

		## force enable
		print_success("Enabling the plugins")
		file = run_command_output("find ~/.mozilla/firefox/*.default*/ -maxdepth 1 -type f -name 'extensions.json' -print -quit").decode("ascii").rstrip()
		file_replace(file, '"active":false,', '"active":true,')
		file_replace(file, '"userDisabled":true,', '"userDisabled:false,')
		#file = run_command_output("find ~/.mozilla/firefox/*.default*/ -maxdepth 1 -type f -name 'extension-settings.json' -print -quit").decode("ascii").rstrip()
		#file_replace(file, '"active":false,', '"active":true,')
		#file_replace(file, '"userDisabled":true,', '"userDisabled:false,')

		## making sure plugins are configured
		run_command('timeout 15 firefox')
		run_command('timeout 5 killall -9 -q -w firefox-esr')
		run_command('sleep 3')
		run_command('timeout 15 firefox')
		run_command('timeout 5 killall -9 -q -w firefox-esr')
		run_command('sleep 3')

		print_success("Plugins enabled and installed! Clearing session")
		run_command("find /root/.mozilla/firefox/*.default*/ -maxdepth 1 -type f -name 'sessionstore.*' -delete")

		print_success("Configuring plugins")
		file = run_command_output("find ~/.mozilla/firefox/*.default*/ -maxdepth 1 -type f -name 'foxyproxy.xml' -print -quit").decode("ascii").rstrip()
		if file_exists(file):
			contents = """
<?xml version="1.0" encoding="UTF-8"?>
<foxyproxy mode="disabled" selectedTabIndex="0" toolbaricon="true" toolsMenu="true" contextMenu="false" advancedMenus="false" previousMode="disabled" resetIconColors="true" useStatusBarPrefix="true" excludePatternsFromCycling="false" excludeDisabledFromCycling="false" ignoreProxyScheme="false" apiDisabled="false" proxyForVersionCheck=""><random includeDirect="false" includeDisabled="false"/><statusbar icon="true" text="false" left="options" middle="cycle" right="contextmenu" width="0"/><toolbar left="options" middle="cycle" right="contextmenu"/><logg enabled="false" maxSize="500" noURLs="false" header="&lt;?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;?&gt;
&lt;!DOCTYPE html PUBLIC &quot;-//W3C//DTD XHTML 1.0 Strict//EN&quot; &quot;http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd&quot;&gt;
&lt;html xmlns=&quot;http://www.w3.org/1999/xhtml&quot;&gt;&lt;head&gt;&lt;title&gt;&lt;/title&gt;&lt;link rel=&quot;icon&quot; href=&quot;http://getfoxyproxy.org/favicon.ico&quot;/&gt;&lt;link rel=&quot;shortcut icon&quot; href=&quot;http://getfoxyproxy.org/favicon.ico&quot;/&gt;&lt;link rel=&quot;stylesheet&quot; href=&quot;http://getfoxyproxy.org/styles/log.css&quot; type=&quot;text/css&quot;/&gt;&lt;/head&gt;&lt;body&gt;&lt;table class=&quot;log-table&quot;&gt;&lt;thead&gt;&lt;tr&gt;&lt;td class=&quot;heading&quot;&gt;${timestamp-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${url-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${proxy-name-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${proxy-notes-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${pattern-name-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${pattern-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${pattern-case-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${pattern-type-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${pattern-color-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${pac-result-heading}&lt;/td&gt;&lt;td class=&quot;heading&quot;&gt;${error-msg-heading}&lt;/td&gt;&lt;/tr&gt;&lt;/thead&gt;&lt;tfoot&gt;&lt;tr&gt;&lt;td/&gt;&lt;/tr&gt;&lt;/tfoot&gt;&lt;tbody&gt;" row="&lt;tr&gt;&lt;td class=&quot;timestamp&quot;&gt;${timestamp}&lt;/td&gt;&lt;td class=&quot;url&quot;&gt;&lt;a href=&quot;${url}&quot;&gt;${url}&lt;/a&gt;&lt;/td&gt;&lt;td class=&quot;proxy-name&quot;&gt;${proxy-name}&lt;/td&gt;&lt;td class=&quot;proxy-notes&quot;&gt;${proxy-notes}&lt;/td&gt;&lt;td class=&quot;pattern-name&quot;&gt;${pattern-name}&lt;/td&gt;&lt;td class=&quot;pattern&quot;&gt;${pattern}&lt;/td&gt;&lt;td class=&quot;pattern-case&quot;&gt;${pattern-case}&lt;/td&gt;&lt;td class=&quot;pattern-type&quot;&gt;${pattern-type}&lt;/td&gt;&lt;td class=&quot;pattern-color&quot;&gt;${pattern-color}&lt;/td&gt;&lt;td class=&quot;pac-result&quot;&gt;${pac-result}&lt;/td&gt;&lt;td class=&quot;error-msg&quot;&gt;${error-msg}&lt;/td&gt;&lt;/tr&gt;" footer="&lt;/tbody&gt;&lt;/table&gt;&lt;/body&gt;&lt;/html&gt;"/><warnings/><autoadd enabled="false" temp="false" reload="true" notify="true" notifyWhenCanceled="true" prompt="true"><match enabled="true" name="Dynamic AutoAdd Pattern" pattern="*://${3}${6}/*" isRegEx="false" isBlackList="false" isMultiLine="false" caseSensitive="false" fromSubscription="false"/><match enabled="true" name="" pattern="*You are not authorized to view this page*" isRegEx="false" isBlackList="false" isMultiLine="true" caseSensitive="false" fromSubscription="false"/></autoadd><quickadd enabled="false" temp="false" reload="true" notify="true" notifyWhenCanceled="true" prompt="true"><match enabled="true" name="Dynamic QuickAdd Pattern" pattern="*://${3}${6}/*" isRegEx="false" isBlackList="false" isMultiLine="false" caseSensitive="false" fromSubscription="false"/></quickadd><defaultPrefs origPrefetch="null"/><proxies><proxy name="localhost:8080" id="1145138293" notes="e.g. Burp, w3af" fromSubscription="false" enabled="true" mode="manual" selectedTabIndex="0" lastresort="false" animatedIcons="true" includeInCycle="false" color="#07753E" proxyDNS="true" noInternalIPs="false" autoconfMode="pac" clearCacheBeforeUse="true" disableCache="true" clearCookiesBeforeUse="false" rejectCookies="false"><matches/><autoconf url="" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><autoconf url="http://wpad/wpad.dat" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><manualconf host="127.0.0.1" port="8080" socksversion="5" isSocks="false" username="" password="" domain=""/></proxy><proxy name="localhost:8081 (socket5)" id="212586674" notes="e.g. SSH" fromSubscription="false" enabled="true" mode="manual" selectedTabIndex="0" lastresort="false" animatedIcons="true" includeInCycle="false" color="#917504" proxyDNS="true" noInternalIPs="false" autoconfMode="pac" clearCacheBeforeUse="true" disableCache="true" clearCookiesBeforeUse="false" rejectCookies="false"><matches/><autoconf url="" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><autoconf url="http://wpad/wpad.dat" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><manualconf host="127.0.0.1" port="8081" socksversion="5" isSocks="true" username="" password="" domain=""/></proxy><proxy name="No Caching" id="3884644610" notes="" fromSubscription="false" enabled="true" mode="system" selectedTabIndex="0" lastresort="false" animatedIcons="true" includeInCycle="false" color="#990DA6" proxyDNS="true" noInternalIPs="false" autoconfMode="pac" clearCacheBeforeUse="true" disableCache="true" clearCookiesBeforeUse="false" rejectCookies="false"><matches/><autoconf url="" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><autoconf url="http://wpad/wpad.dat" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><manualconf host="" port="" socksversion="5" isSocks="false" username="" password="" domain=""/></proxy><proxy name="Default" id="3377581719" notes="" fromSubscription="false" enabled="true" mode="direct" selectedTabIndex="0" lastresort="true" animatedIcons="false" includeInCycle="true" color="#0055E5" proxyDNS="true" noInternalIPs="false" autoconfMode="pac" clearCacheBeforeUse="false" disableCache="false" clearCookiesBeforeUse="false" rejectCookies="false"><matches><match enabled="true" name="All" pattern="*" isRegEx="false" isBlackList="false" isMultiLine="false" caseSensitive="false" fromSubscription="false"/></matches><autoconf url="" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><autoconf url="http://wpad/wpad.dat" loadNotification="true" errorNotification="true" autoReload="false" reloadFreqMins="60" disableOnBadPAC="true"/><manualconf host="" port="" socksversion="5" isSocks="false" username="" password=""/></proxy></proxies></foxyproxy>
"""
			file_write(file, contents)
			print_success("Done")


	## Install metasploit
	do_action("Installing and configuring metasploit")
	run_command("apt -y -qq install metasploit-framework")
	run_command('mkdir -p /root/.msf4/modules/{auxiliary,exploits,payloads,post}/')
	run_command('systemctl stop postgresql')
	run_command('systemctl start postgresql')
	run_command('msfdb reinit')
	run_command('sleep 5')
	contents = """
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
	file_write('/root/.msf4/msfconsole.rc', contents)
	print_success("Done")



	## Running metasploit db
	do_action("Starting metasploit for the first time.  This will take 6 minutes!")
	run_command('echo "Started at: $(date)"', False, True)
	run_command("systemctl start postgresql")
	run_command("msfdb start")
	run_command("msfconsole -q -x 'version;db_status;sleep 310; exit'")
	print_success("Done")


	## Install exe2hex
	do_action("Installing exe2hex")
	run_command('apt -y -qq install exe2hexbat', True)
	print_success("Done")

	## Install msfpc
	do_action("Installing msfpc")
	run_command('apt -y -qq install msfpc', True)
	print_success("Done")

	## Install gedit
	do_action("Installing Gedit")
	run_command('apt -y -qq install gedit', True)
	print_success("Done")

	## Install go
	do_action("Installing Go")
	run_command('apt -y -qq install golang', True)
	print_success("Done")

	## Install libreoffice
	do_action("Installing Libreoffice")
	run_command('apt -y -qq install libreoffice', True)
	print_success("Done")


	## Install ftp
	do_action("Installing ftp")
	run_command('apt -y -qq install ftp', True)
	print_success("Done")

	## Install exe2hex
	do_action("Installing CA certificates")
	run_command('apt -y -qq install ca-certificates', True)
	print_success("Done")

	## Install filezilla
	do_action("Installing Filezilla")
	run_command('apt -y -qq install filezilla', True)
	print_success("Done")

	## Install compressions
	do_action("Installing compressors and decompressors")
	run_command('apt -y -qq install zip unzip p7zip-full', True)
	print_success("Done")

	## Install aircrack
	do_action("Installing aircrack suite")
	run_command('apt -y -qq install aircrack-ng curl', True)
	run_command('airodump-ng-oui-update')
	print_success("Done")

	## Install reaver
	do_action("Installing reaver")
	run_command('apt -y -qq install reaver pixiewps', True)
	print_success("Done")

	## Install vulnscan for nmap
	do_action("Installing nmap vulnscan")
	run_command('apt -y -qq install nmap curl', True)
	file_download('http://www.computec.ch/projekte/vulscan/download/nmap_nse_vulscan-2.0.tar.gz', '/root/nmap_nse_vulnscan.tar.gz')
	run_command('cd /root; gunzip /root/nmap_nse_vulnscan.tar.gz')
	run_command('tar -xf /root/nmap_nse_vulnscan.tar -C /usr/share/nmap/scripts/')
	run_command('chmod -R 0755 /usr/share/nmap/scripts/; find /usr/share/nmap/scripts/ -type f -exec chmod 0644 {} \;')
	run_command('rm /root/nmap_nse_vulnscan.tar')
	print_success("Done")



	## Install proxychains-ng
	do_action("Installing proxychains-ng")
	run_command('apt -y -qq install git gcc', True)
	run_command('git clone -q -b master https://github.com/rofl0r/proxychains-ng.git /opt/proxychains-ng-git/')
	run_command('cd /opt/proxychains-ng-git/; git pull -q')
	run_command('cd /opt/proxychains-ng-git/; make -s clean')
	run_command('cd /opt/proxychains-ng-git/; ./configure --prefix=/usr --sysconfdir=/etc')
	run_command('cd /opt/proxychains-ng-git/; make -s')
	run_command('cd /opt/proxychains-ng-git/; make -s install')
	run_command('mkdir -p /usr/local/bin/')
	run_command('ln -sf /usr/bin/proxychains4 /usr/local/bin/proxychains-ng')
	print_success("Done")


	## Install compiling libraries
	do_action("Installing compiling libraries")
	run_command("apt -y -qq install gcc g++ gcc-multilib make automake libc6 libc6-i386 libc6-i686 build-essential dpkg-dev", True, True)
	print_success("Done")


	## Install mingw libraries
	do_action("Installing MinGW")
	run_command("apt -y -qq install mingw-w64 binutils-mingw-w64 gcc-mingw-w64 cmake mingw-w64-i686-dev mingw-w64-x86-64-dev mingw-w64-tools gcc-mingw-w64-i686 gcc-mingw-w64-x86-64", True)
	print_success("Done")

	## Install wine
	do_action("Installing Wine")
	run_command("apt -y -qq install wine winetricks", True)
	run_command('dpkg --add-architecture i386')
	run_command('apt -qq update')
	run_command('apt -y -qq install wine32')
	print_success("Done")


	## Install wordlists
	do_action("Installing Wordlists")
	run_command("apt -y -qq install wordlists curl", True)
	print_success("Done")

	## Install xfreerdp
	do_action("Installing freerdp")
	run_command("apt -y -qq install freerdp2-x11", True)
	print_success("Done")

	## Install xprobe
	do_action("Installing xprobe")
	run_command("apt -y -qq install xprobe", True)
	print_success("Done")

	## Install p0f
	do_action("Installing p0f")
	run_command("apt -y -qq install p0f", True)
	print_success("Done")

	## Install nbtscan
	do_action("Installing nbtscan")
	run_command("apt -y -qq install nbtscan", True)
	print_success("Done")

	## Install samba
	do_action("Installing samba")
	run_command("apt -y -qq install samba cifs-utils", True)
	run_command("groupdel smbgroup")
	run_command("groupadd smbgroup")
	run_command("userdel samba")
	run_command("useradd -r -M -d /nonexistent -s /bin/false -c 'Samba User' -g smbgroup samba")
	file_backup('/etc/samba/smb.conf')
	file_append_or_replace('/etc/samba/smb.conf', 'guest account = .*', 'guest account = samba')
	contents = """
[shared]
  comment = Shared
  path = /var/samba/
  browseable = yes
  guest ok = yes
  #guest only = yes
  read only = no
  writable = yes
  create mask = 0644
  directory mask = 0755
	"""
	if not file_contains('/etc/samba/smb.conf', '[shared]'):
		file_append('/etc/samba/smb.conf', contents)
	run_command('mkdir -p /var/samba/')
	run_command('chown -R samba:smbgroup /var/samba/')
	run_command('chmod -R 0755 /var/samba/')
	run_command('touch /etc/printcap')
	run_command('systemctl stop samba')
	run_command('systemctl disable samba')
	print_success("Done")

	## Install apache2 & php & mysql
	do_action("Installing Apache, PHP, and MySQL")
	run_command("apt -y -qq install apache2 php php-cli php-curl libapache2-mod-php default-mysql-server php-mysql", True)
	run_command('echo "It works" > /var/www/html/index.html')
	print_success("Done")

	## Install sshpass
	do_action("Installing sshpass")
	run_command("apt -y -qq install sshpass", True)
	print_success("Done")

	## Install dbeaver
	do_action("Installing dbeaver")
	run_command("apt -y -qq install sshpass", True)
	file_download('http://dbeaver.jkiss.org/files/dbeaver-ce_latest_amd64.deb', '/root/dbeaver.deb')
	run_command('dpkg -i /root/dbeaver.deb')
	run_command('ln -sf /usr/share/dbeaver/dbeaver /usr/local/.bin/dbeaver')
	run_command('rm /root/dbeaver.deb')
	print_success("Done")

	## Install sshpass
	do_action("Installing ssh server")
	run_command("apt -y -qq install openssh-server", True)
	if not file_exists('/root/.ssh/id_rsa'):
		run_command('ssh-keygen -b 4096 -t rsa -f ~/.ssh/id_rsa -P ""')
	file_replace('/etc/ssh/sshd_config', '^.*PermitRootLogin .*', 'PermitRootLogin yes')
	print_success("Done")

	## Installing github repos
	do_action("Installing various github tools into /opt")
	install_githubs()
	print_success("Done")

	## Installing oracle JDK
	do_action("Installing Oracle JDK instead of OpenJDK")
	jdk_link = run_command_output('curl -s "https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html" | grep \'linux-x64.tar.gz\' | head -n 1 | awk -F, \'{print $3}\' | awk -F\'":\' \'{print $2}\' | tr -d \'"\'').decode("ascii").rstrip()
	run_command('wget --no-check-certificate --no-cookies --header "Cookie: oraclelicense=accept-securebackup-cookie" "{0}" -O /root/jdk.tar.gz'.format(jdk_link))
	run_command('cd /root/; tar -xzvf /root/jdk.tar.gz -C /opt/')
	run_command('rm /root/jdk.tar.gz')
	jdk_dir = run_command_output('ls -a /opt/ | grep jdk | head -n 1').decode("ascii").rstrip()
	run_command('update-alternatives --install /usr/bin/java java /opt/{0}/bin/java 1'.format(jdk_dir))
	run_command('update-alternatives --install /usr/bin/javac javac /opt/{0}/bin/javac 1'.format(jdk_dir))
	run_command('update-alternatives --install /usr/lib/mozilla/plugins/libjavaplugin.so mozilla-javaplugin.so /opt/{0}/jre/lib/amd64/libnpjp2.so 1'.format(jdk_dir))
	run_command('update-alternatives --set java /opt/{0}/bin/java'.format(jdk_dir))
	run_command('update-alternatives --set javac /opt/{0}/bin/javac'.format(jdk_dir))
	run_command('update-alternatives --set mozilla-javaplugin.so /opt/{0}/jre/lib/amd64/libnpjp2.so'.format(jdk_dir))

	## Installing Cobalt Strike
	do_action("Installing Cobalt Strike into /opt (if license is provided)")
	if COBALTSTRIKE_LICENSE == "":
		print_success("No cobalt strike license provided.  Skipping!")
	else:
		cs_link = run_command_output("curl -s --data 'dlkey={0}' 'https://cobaltstrike.com/download' | grep -m 1 -oP '(downloads/[a-z0-9]{{32}}/cobaltstrike-trial)'".format(COBALTSTRIKE_LICENSE)).decode("ascii").rstrip()
		if cs_link == "":
			print_error("Cobalt strike license is invalid! Skipping...")
			COBALTSTRIKE_LICENSE = ""
		else:
			print_success("License is valid! Downloading package...")
			file_download("https://cobaltstrike.com/{0}.tgz".format(cs_link), "/root/cobaltstrike.tgz")
			run_command("tar -zxf /root/cobaltstrike.tgz -C /opt/")
			run_command("rm /root/cobaltstrike.tgz")
			file_write("/root/.cobaltstrike.license", COBALTSTRIKE_LICENSE)
			print_success("Installed....now updating from the trial version")
			run_command("cd /opt/cobaltstrike/; ./update")
			print_success("Done")

	## Installing Cobalt Strike scripts
	do_action("Installing Cobalt Strike scripts")
	run_command("mkdir -p /opt/cs_scripts")
	cs_script_repos = [
		'killswitch-GUI/CobaltStrike-ToolKit',
		'kussic/CS-KickassBot',
		'ZonkSec/persistence-aggressor-script',
		'harleyQu1nn/AggressorScripts',
		'ramen0x3f/AggressorScripts',
	]
	for repo in cs_script_repos:
		repo_name = repo.replace('/','_').lower() + '-git'
		run_command("git clone -q -b master https://github.com/{0}.git /opt/cs_scripts/{1}".format(repo, repo_name))
		run_command("cd /opt/cs_scripts/{0}/; git pull -q".format(repo_name))
	if COBALTSTRIKE_LICENSE != "":
		run_command("ln -sf /opt/cs_scripts/ /opt/cobaltstrike/scripts")
	print_success("Done")

	## Writing update script
	do_action("Writing GitHub update script")
	content = """#!/bin/bash

for d in /opt/* ; do
    echo "Starting $d"
    pushd $d &> /dev/null
    git fetch
    git pull origin master
    popd &> /dev/null
done
for d in /opt/cs_scripts/* ; do
    echo "Starting $d"
    pushd $d &> /dev/null
    git fetch
    git pull origin master
    popd &> /dev/null
done
	"""
	file_write('/opt/UpdateAll.sh', content)
	run_command('chmod +x /opt/UpdateAll.sh')
	print_success('Done')

	## Remove gnome shell if installed xfce4 - THIS MUST BE LAST
	if INSTALL_NEW_DE:
		## Removing gnome shell
		do_action("Removing Gnome")
		run_command('apt -y -qq remove gnome-shell')
		print_success("Done")


def do_action(description):
	global TOTAL_PARTS, CURRENT_STAGE
	CURRENT_STAGE += 1
	print(Fore.GREEN + "[+]" + Fore.RESET + " {0}/{1} - {2}...".format(CURRENT_STAGE, TOTAL_PARTS, description))

def print_success(msg):
	print(Fore.GREEN + "    " + msg + Fore.RESET)

def print_error(msg):
	print(Fore.RED + "[!] ERROR:    " + msg + Fore.RESET)

def run_command(cmd, print_if_error=False, show_output = False):
	if not show_output:
		cmd += " > /dev/null 2>&1"
	#print("RUNNING: " + cmd)
	ret = os.system(cmd)
	if print_if_error and ret != 0:
		print_error("Failed running \"{0}\"".format(cmd))
	return ret

def run_command_output(cmd):
	return subprocess.check_output(cmd, shell=True)

def file_read(filename):
	if not file_exists(filename):
		return ""
	contents = ""
	with open(filename, 'r') as new_file:
		contents = new_file.read().replace('\n',"\n")
	return contents

def file_exists(filename):
	return os.path.exists(filename)

def file_contains(filename, text):
	return text in file_read(filename)

def file_write(filename, contents):
	with open(filename, 'w') as f:
		f.write(contents)

def file_append(filename, contents):
	with open(filename, 'a') as f:
		f.write(contents+"\n")

def file_append_once(filename, contents, search=""):
	if search == "":
		search = contents
	if not file_contains(filename, search):
		file_append(filename, contents)

def file_replace(filename, find, replace):
	newText = file_read(filename)
	newText = re.sub(find, replace, newText, flags=re.M)
	file_write(filename, newText)

def file_append_or_replace(filename, find, replace):
	file_replace(filename, find, replace)
	file_append_once(filename, replace)

def file_backup(filename):
	if file_exists(filename):
		run_command('cp -n {0} {0}.bkup'.format(filename))

def file_download(location, destination):
	os.system("wget -O '{0}' '{1}' > /dev/null 2>&1".format(destination, location))



######### HELPER FUNCTIONS

def configure_xfce():
	global HIDPI_MONITOR
	## install axiomd theme
	run_command("mkdir -p /root/.themes")
	file_download('https://www.dropbox.com/s/6b3ccbnbbvg3ij4/90145-axiom.tar.gz?dl=1', '/root/axiom.tar.gz')
	run_command('cd /root/; tar xfs /root/axiom.tar.gz')
	run_command('mv /root/axiom /root/axiomd /root/.themes')
	run_command('rm /root/axiom.tar.gz')
	run_command('rm -r /root/axiom /root/axiomd')
	run_command("mkdir -p ~/.config/xfce4/panel/launcher-{2,4,5,6,7,8,9}/")
	run_command("mkdir -p ~/.config/xfce4/xfconf/xfce-perchannel-xml/")
	## keybindings
	contents = """<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-keyboard-shortcuts" version="1.0">
  <property name="commands" type="empty">
    <property name="custom" type="empty">
      <property name="XF86Display" type="string" value="xfce4-display-settings --minimal"/>
      <property name="&lt;Alt&gt;F2" type="string" value="xfrun4"/>
      <property name="&lt;Primary&gt;space" type="string" value="xfce4-appfinder"/>
      <property name="&lt;Primary&gt;&lt;Alt&gt;t" type="string" value="/usr/bin/exo-open --launch TerminalEmulator"/>
      <property name="&lt;Primary&gt;&lt;Alt&gt;Delete" type="string" value="xflock4"/>
      <property name="&lt;Primary&gt;Escape" type="string" value="xfdesktop --menu"/>
      <property name="&lt;Super&gt;p" type="string" value="xfce4-display-settings --minimal"/>
      <property name="override" type="bool" value="true"/>
    </property>
  </property>
  <property name="xfwm4" type="empty">
    <property name="custom" type="empty">
      <property name="&lt;Alt&gt;&lt;Control&gt;End" type="string" value="move_window_next_workspace_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;Home" type="string" value="move_window_prev_workspace_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_1" type="string" value="move_window_workspace_1_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_2" type="string" value="move_window_workspace_2_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_3" type="string" value="move_window_workspace_3_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_4" type="string" value="move_window_workspace_4_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_5" type="string" value="move_window_workspace_5_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_6" type="string" value="move_window_workspace_6_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_7" type="string" value="move_window_workspace_7_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_8" type="string" value="move_window_workspace_8_key"/>
      <property name="&lt;Alt&gt;&lt;Control&gt;KP_9" type="string" value="move_window_workspace_9_key"/>
      <property name="&lt;Alt&gt;&lt;Shift&gt;Tab" type="string" value="cycle_reverse_windows_key"/>
      <property name="&lt;Alt&gt;Delete" type="string" value="del_workspace_key"/>
      <property name="&lt;Alt&gt;F10" type="string" value="maximize_window_key"/>
      <property name="&lt;Alt&gt;F11" type="string" value="fullscreen_key"/>
      <property name="&lt;Alt&gt;F12" type="string" value="above_key"/>
      <property name="&lt;Alt&gt;F4" type="string" value="close_window_key"/>
      <property name="&lt;Alt&gt;F6" type="string" value="stick_window_key"/>
      <property name="&lt;Alt&gt;F7" type="string" value="move_window_key"/>
      <property name="&lt;Alt&gt;F8" type="string" value="resize_window_key"/>
      <property name="&lt;Alt&gt;F9" type="string" value="hide_window_key"/>
      <property name="&lt;Alt&gt;Insert" type="string" value="add_workspace_key"/>
      <property name="&lt;Alt&gt;space" type="string" value="popup_menu_key"/>
      <property name="&lt;Alt&gt;Tab" type="string" value="cycle_windows_key"/>
      <property name="&lt;Control&gt;&lt;Alt&gt;d" type="string" value="show_desktop_key"/>
      <property name="&lt;Control&gt;&lt;Alt&gt;Down" type="string" value="down_workspace_key"/>
      <property name="&lt;Control&gt;&lt;Alt&gt;Left" type="string" value="left_workspace_key"/>
      <property name="&lt;Control&gt;&lt;Alt&gt;Right" type="string" value="right_workspace_key"/>
      <property name="&lt;Control&gt;&lt;Alt&gt;Up" type="string" value="up_workspace_key"/>
      <property name="&lt;Control&gt;&lt;Shift&gt;&lt;Alt&gt;Left" type="string" value="move_window_left_key"/>
      <property name="&lt;Control&gt;&lt;Shift&gt;&lt;Alt&gt;Right" type="string" value="move_window_right_key"/>
      <property name="&lt;Control&gt;&lt;Shift&gt;&lt;Alt&gt;Up" type="string" value="move_window_up_key"/>
      <property name="&lt;Control&gt;F1" type="string" value="workspace_1_key"/>
      <property name="&lt;Control&gt;F10" type="string" value="workspace_10_key"/>
      <property name="&lt;Control&gt;F11" type="string" value="workspace_11_key"/>
      <property name="&lt;Control&gt;F12" type="string" value="workspace_12_key"/>
      <property name="&lt;Control&gt;F2" type="string" value="workspace_2_key"/>
      <property name="&lt;Control&gt;F3" type="string" value="workspace_3_key"/>
      <property name="&lt;Control&gt;F4" type="string" value="workspace_4_key"/>
      <property name="&lt;Control&gt;F5" type="string" value="workspace_5_key"/>
      <property name="&lt;Control&gt;F6" type="string" value="workspace_6_key"/>
      <property name="&lt;Control&gt;F7" type="string" value="workspace_7_key"/>
      <property name="&lt;Control&gt;F8" type="string" value="workspace_8_key"/>
      <property name="&lt;Control&gt;F9" type="string" value="workspace_9_key"/>
      <property name="&lt;Shift&gt;&lt;Alt&gt;Page_Down" type="string" value="lower_window_key"/>
      <property name="&lt;Shift&gt;&lt;Alt&gt;Page_Up" type="string" value="raise_window_key"/>
      <property name="&lt;Super&gt;Tab" type="string" value="switch_window_key"/>
      <property name="Down" type="string" value="down_key"/>
      <property name="Escape" type="string" value="cancel_key"/>
      <property name="Left" type="string" value="left_key"/>
      <property name="Right" type="string" value="right_key"/>
      <property name="Up" type="string" value="up_key"/>
      <property name="override" type="bool" value="true"/>
      <property name="&lt;Super&gt;Left" type="string" value="tile_left_key"/>
      <property name="&lt;Super&gt;Right" type="string" value="tile_right_key"/>
      <property name="&lt;Super&gt;Up" type="string" value="maximize_window_key"/>
    </property>
  </property>
  <property name="providers" type="array">
    <value type="string" value="xfwm4"/>
    <value type="string" value="commands"/>
  </property>
</channel>"""
	file_write('/root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-keyboard-shortcuts.xml', contents)

	# power options
	contents = """<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-power-manager" version="1.0">
  <property name="xfce4-power-manager" type="empty">
    <property name="power-button-action" type="empty"/>
    <property name="dpms-enabled" type="bool" value="true"/>
    <property name="blank-on-ac" type="int" value="0"/>
    <property name="dpms-on-ac-sleep" type="uint" value="0"/>
    <property name="dpms-on-ac-off" type="uint" value="0"/>
  </property>
</channel>"""
	file_write('/root/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-power-manager.xml', contents)
	run_command('nohup xfce4-power-manager')

	# set desktop files
	run_command('ln -sf /usr/share/applications/exo-terminal-emulator.desktop ~/.config/xfce4/panel/launcher-2/exo-terminal-emulator.desktop')
	run_command('ln -sf /usr/share/applications/kali-wireshark.desktop        ~/.config/xfce4/panel/launcher-4/kali-wireshark.desktop')
	run_command('ln -sf /usr/share/applications/firefox-esr.desktop           ~/.config/xfce4/panel/launcher-5/firefox-esr.desktop')
	run_command('ln -sf /usr/share/applications/kali-burpsuite.desktop        ~/.config/xfce4/panel/launcher-6/kali-burpsuite.desktop')
	run_command('ln -sf /usr/share/applications/kali-msfconsole.desktop       ~/.config/xfce4/panel/launcher-7/kali-msfconsole.desktop')
	run_command('ln -sf /usr/share/applications/org.gnome.gedit.desktop       ~/.config/xfce4/panel/launcher-8/textedit.desktop')
	run_command('ln -sf /usr/share/applications/xfce4-appfinder.desktop       ~/.config/xfce4/panel/launcher-9/xfce4-appfinder.desktop')


	# panel settings
	run_command('xfconf-query -n -a -c xfce4-panel -p /panels -t int -s 0')
	run_command('xfconf-query --create --channel xfce4-panel --property /panels/panel-0/plugin-ids -t int -s 1   -t int -s 2   -t int -s 3   -t int -s 4   -t int -s 5 -t int -s 7   -t int -s 8  -t int -s 9 -t int -s 10  -t int -s 11  -t int -s 13  -t int -s 15  -t int -s 16  -t int -s 17  -t int -s 19  -t int -s 20')
	run_command('xfconf-query -n -c xfce4-panel -p /panels/panel-0/length -t int -s 100')
	run_command('xfconf-query -n -c xfce4-panel -p /panels/panel-0/size -t int -s 30')
	run_command('xfconf-query -n -c xfce4-panel -p /panels/panel-0/position -t string -s "p=6;x=0;y=0"')
	run_command('xfconf-query -n -c xfce4-panel -p /panels/panel-0/position-locked -t bool -s true')
	# application menu
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-1 -t string -s applicationsmenu')
	# terminal   ID: exo-terminal-emulator
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-2 -t string -s launcher')
	# places
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-3 -t string -s places')
	# wireshark  ID: kali-wireshark
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-4 -t string -s launcher')
	# firefox    ID: firefox-esr
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-5 -t string -s launcher')
	# msf        ID: kali-msfconsole
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-7 -t string -s launcher')
	# gedit      ID: org.gnome.gedit.desktop
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-8 -t string -s launcher')
	# search     ID: xfce4-appfinder
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-9 -t string -s launcher')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-10 -t string -s tasklist')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-11 -t string -s separator')
	# audio
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-13 -t string -s mixer')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-15 -t string -s systray')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-16 -t string -s actions')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-17 -t string -s clock')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-19 -t string -s pager')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-20 -t string -s showdesktop')
	#--- application menu
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-1/show-tooltips -t bool -s true')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-1/show-button-title -t bool -s false')
	#--- terminal
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-2/items -t string -s "exo-terminal-emulator.desktop" -a')
	#--- places
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-3/mount-open-volumes -t bool -s true')
	#--- wireshark
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-4/items -t string -s "kali-wireshark.desktop" -a')
	#--- firefox
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-5/items -t string -s "firefox-esr.desktop" -a')
	#--- metasploit
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-7/items -t string -s "kali-msfconsole.desktop" -a')
	#--- gedit
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-8/items -t string -s "textedit.desktop" -a')
	#--- search
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-9/items -t string -s "xfce4-appfinder.desktop" -a')
	#--- tasklist (& separator - required for padding)
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-10/show-labels -t bool -s true')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-10/show-handle -t bool -s false')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-11/style -t int -s 0')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-11/expand -t bool -s true')
	#--- systray
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-15/show-frame -t bool -s false')
	#--- actions
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-16/appearance -t int -s 1')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-16/items -t string -s "+logout-dialog"  -t string -s "-switch-user"  -t string -s "-separator" -t string -s "-logout"  -t string -s "+lock-screen"  -t string -s "+hibernate"  -t string -s "+suspend"  -t string -s "+restart"  -t string -s "+shutdown"  -a')
	#--- clock
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-17/show-frame -t bool -s false')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-17/mode -t int -s 2')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-17/digital-format -t string -s "%R, %Y-%m-%d"')
	#--- pager / workspace
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-19/miniature-view -t bool -s true')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-19/rows -t int -s 1')
	run_command('xfconf-query -n -c xfwm4 -p /general/workspace_count -t int -s 3')
	#--- Theme options
	run_command('xfconf-query -n -c xsettings -p /Net/ThemeName -s "axiomd"')
	run_command('xfconf-query -n -c xsettings -p /Net/IconThemeName -s "Tango"')
	run_command('xfconf-query -n -c xsettings -p /Gtk/MenuImages -t bool -s true')
	run_command('xfconf-query -n -c xfce4-panel -p /plugins/plugin-1/button-icon -t string -s "kali-menu"')
	#--- Window management
	run_command('xfconf-query -n -c xfwm4 -p /general/snap_to_border -t bool -s true')
	run_command('xfconf-query -n -c xfwm4 -p /general/snap_to_windows -t bool -s true')
	run_command('xfconf-query -n -c xfwm4 -p /general/wrap_windows -t bool -s false')
	run_command('xfconf-query -n -c xfwm4 -p /general/wrap_workspaces -t bool -s false')
	run_command('xfconf-query -n -c xfwm4 -p /general/click_to_focus -t bool -s false')
	run_command('xfconf-query -n -c xfwm4 -p /general/click_to_focus -t bool -s true')
	#--- Hide icons
	run_command('xfconf-query -n -c xfce4-desktop -p /desktop-icons/file-icons/show-filesystem -t bool -s false')
	run_command('xfconf-query -n -c xfce4-desktop -p /desktop-icons/file-icons/show-home -t bool -s false')
	run_command('xfconf-query -n -c xfce4-desktop -p /desktop-icons/file-icons/show-trash -t bool -s false')
	run_command('xfconf-query -n -c xfce4-desktop -p /desktop-icons/file-icons/show-removable -t bool -s false')
	#--- Start and exit values
	run_command('xfconf-query -n -c xfce4-session -p /splash/Engine -t string -s ""')
	run_command('xfconf-query -n -c xfce4-session -p /shutdown/LockScreen -t bool -s true')
	run_command('xfconf-query -n -c xfce4-session -p /general/SaveOnExit -t bool -s false')
	#--- App Finder
	run_command('xfconf-query -n -c xfce4-appfinder -p /last/pane-position -t int -s 248')
	run_command('xfconf-query -n -c xfce4-appfinder -p /last/window-height -t int -s 742')
	run_command('xfconf-query -n -c xfce4-appfinder -p /last/window-width -t int -s 648')
	#--- Enable compositing
	run_command('xfconf-query -n -c xfwm4 -p /general/use_compositing -t bool -s true')
	run_command('xfconf-query -n -c xfwm4 -p /general/frame_opacity -t int -s 100')

	## If its a hidpi monitor, set the proper values
	if HIDPI_MONITOR:
		run_command('xfconf-query -n -c xsettings -p /Xft/DPI -t int -s 180')
		run_command('xfconf-query -n -c xfce4-panel -p /panels/panel-0/size -t int -s 47')
		run_command('xfconf-query -n -c xfce4-desktop -p /desktop-icons/icon-size -t int -s 90')
		run_command('xfconf-query -n -c xsettings -p /Gtk/IconSizes -t string -s "gtk-large-toolbar=32,32:gtk-small-toolbar=24,24:gtk-menu=32,32:gtk-dialog=88,88:gtk-button=32,32:gtk-dnd=32,32"')
		run_command('xfconf-query -n -c xfwm4 -p /general/theme -t string -s "Default-xhdpi"')
		run_command('xfconf-query -n -c xfwm4 -p /general/title_font -t string -s "Sans Bold 10"')


	# remove mail reader from menu
	file_append_or_replace('/usr/share/applications/exo-mail-reader.desktop', '^NotShowIn=*', 'NotShowIn=XFCE;')

	# set default applications
	run_command('mkdir -p /root/.local/share/applications')
	file_backup('/root/.local/share/applications/mimeapps.list')
	contents = """[Added Associations]
x-scheme-handler/http=exo-web-browser.desktop
x-scheme-handler/https=exo-web-browser.desktop
x-scheme-handler/file=exo-file-manager.desktop
x-scheme-handler/trash=exo-file-manager.desktop
"""
	file_write('/root/.local/share/applications/mimeapps.list', contents)
	file_backup('/root/.config/xfce4/helpers.rc')
	file_write('/root/.config/xfce4/helpers.rc', 'FileManager=Thunar')

	# get wallpaper and set it
	run_command('mkdir -p /usr/share/wallpapers')
	file_download('https://lh5.googleusercontent.com/-CW1-qRVBiqc/U7ARd2T9LCI/AAAAAAAAAGw/oantfR6owSg/w1920-h1080/vzex.png', '/usr/share/wallpapers/kali_blue_splat.png')
	run_command('xfconf-query -n -c xfce4-desktop -p /backdrop/screen0/monitor0/image-show -t bool -s true')
	run_command('xfconf-query -n -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -t string -s "/usr/share/wallpapers/kali_blue_splat.png"')
	run_command('xfconf-query -n -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -t string -s "/usr/share/wallpapers/kali_blue_splat.png"')
	run_command('/usr/bin/dconf write /org/gnome/desktop/screensaver/picture-uri "\'file:///usr/share/wallpapers/kali_blue_splat.png\'"')
	run_command('/usr/bin/dconf write /org/gnome/desktop/screensaver/picture-uri "\'file:///usr/share/wallpapers/kali_blue_splat.png\'"')
	run_command('/usr/bin/xfdesktop --reload 2>/dev/null &')


	# make default DE
	run_command('update-alternatives --set x-session-manager /usr/bin/xfce4-session')


def install_githubs():
	projects = [
		'T-S-A/smbspider',
		'byt3bl33d3r/CrackMapExec',
		'gojhonny/CredCrack',
		'PowerShellEmpire/Empire',
		'jekyc/wig',
		'Dionach/CMSmap',
		'droope/droopescan',
		'ChrisTruncer/EyeWitness',
		'adaptivethreat/BloodHound',
		'lgandx/Responder',
		'ChrisTruncer/Just-Metadata',
		'ChrisTruncer/Egress-Assess',
		'Raikia/CredNinja',
		'Raikia/SMBCrunch',
		'Raikia/IPCheckScope',
		'secretsquirrel/SigThief',
		'enigma0x3/Misc-PowerShell-Stuff',
		'0x09AL/raven',
		'dafthack/MailSniper',
		'Arvanaghi/CheckPlease',
		'trustedsec/ptf',
		'Mr-Un1k0d3r/PowerLessShell',
		'Mr-Un1k0d3r/CatMyFish',
		'Mr-Un1k0d3r/MaliciousMacroGenerator',
		'Veil-Framework/Veil',
	]

	additional_instructions = {
		'Raikia/CredNinja': ['ln -s /usr/local/bin/credninja CredNinja.py'],
		'PowerShellEmpire/Empire': ['export STAGING_KEY=random; cd ./setup; bash ./install.sh'],
		'ChrisTruncer/EyeWitness': ['cd ./setup/; bash ./setup.sh'],
	}

	for proj in projects:
		project_name = proj.split('/')[1].lower()
		run_command('git clone -q -b master https://github.com/{0}.git /opt/{1}-git'.format(proj, project_name))
		run_command('cd /opt/{0}-git; git pull -q'.format(project_name))
		if proj in additional_instructions:
			for instr in additional_instructions[proj]:
				run_command('cd /opt/{0}-git; {1}'.format(project_name, instr))




if __name__ == '__main__':
	main()
