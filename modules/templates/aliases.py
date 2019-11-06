#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _LOCAL_ALIAS = """
## grc diff
alias diff='/usr/bin/grc diff'

## grc dig
alias dig='/usr/bin/grc dig'

## grc gcc
alias gcc='/usr/bin/grc gcc'

## grc ifconfig
alias ifconfig='/usr/bin/grc ifconfig'

## grc mount
alias mount='/usr/bin/grc mount'

## grc netstat
alias netstat='/usr/bin/grc netstat'

## grc ping
alias ping='/usr/bin/grc ping'

## grc ps
alias ps='/usr/bin/grc ps'

## grc tail
alias tail='/usr/bin/grc tail'

## grc traceroute
alias traceroute='/usr/bin/grc traceroute'

## grep aliases
alias grep="grep --color=auto"
alias ngrep="grep -n"

alias egrep="egrep --color=auto"

alias fgrep="fgrep --color=auto"

## tmux
alias tmuxr="tmux attach || tmux new"

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
alias nmap="nmap --reason --stats-every 3m --max-retries 1 --max-scan-delay 20 "

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

    def check(self, config):
        return True

    def install(self, config):
        print_status("Configuring global aliases", 1)
        file_backup('/etc/bash.bashrc')
        file_append_or_replace('/etc/bash.bashrc', '.*force_color_prompt=.*', 'force_color_prompt=yes')
        file_append_once('/etc/bash.bashrc', 'PS1=\'${debian_chroot:+($debian_chroot)}\\[\\033[01;31m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ \'')
        file_append_once('/etc/bash.bashrc', "export LS_OPTIONS='--color=auto'")
        file_append_once('/etc/bash.bashrc', 'eval "$(dircolors)"')
        file_append_once('/etc/bash.bashrc', "alias ls='ls $LS_OPTIONS'")
        file_append_once('/etc/bash.bashrc', "alias ll='ls $LS_OPTIONS -l'")
        file_append_once('/etc/bash.bashrc', "alias l='ls $LS_OPTIONS -lA'")
        file_replace('/etc/bash.bashrc', '#alias', 'alias')
        print_success("Done", 1)

        print_status("Installing grc", 1)
        apt_install("grc")
        print_success("Done", 1)

        print_status("Configuring local aliases")
        file_write('/root/.aliases', self._LOCAL_ALIAS)
        run_command('touch /root/.aliases')
        file_replace('/root/.bashrc', '#alias', 'alias')
        file_replace('/root/.aliases', '#alias', 'alias')
        file_append_once('/root/.bashrc', "if [ -f ~/.aliases ]; then\n. ~/.aliases\nfi", '~/.aliases')