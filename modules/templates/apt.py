#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _REPOS_TO_ADD = {
        "mongodb-org-4.2": "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main",
        "sublime-text": "deb https://download.sublimetext.com/ apt/stable/",
    }

    _PACKAGES = {
        "APT HTTPS": ["apt-transport-https"],
        "gnupg": ['gnupg'],
        "grc": ['grc'],
        "bash completion": ['bash-completion'],
        "compiling libraries": ['gcc', 'g++', 'gcc-multilib', 'make', 'automake', 'libc6', 'libc6-i386', 'libc6-i686', 'build-essential', 'dpkg-dev'],
        "tmux": ["tmux"],
        "ftp": ["ftp"],
        "exe2hex": ["exe2hexbat"],
        "msfpc": ["msfpc"],
        "gedit": ["gedit"],
        "Go": ["golang"],
        "Libreoffice": ["libreoffice"],
        "CA certificates": ["ca-certificates"],
        "Filezilla": ["filezilla"],
        "Compressors and decompressors": ["unzip", "zip", "p7zip-full"],
        "Aircrack suite": ["aircrack-ng curl"],
        "reaver": ["reaver", "pixiewps"],
        "redis": ["redis-tools"],
        "MongoDB Tools": ["mongodb-org-tools"],
        "nmap": ["nmap"],
        "MinGW": ["mingw-w64", "binutils-mingw-w64", "gcc-mingw-w64", "cmake", "mingw-w64-i686-dev", "mingw-w64-x86-64-dev", "mingw-w64-tools", "gcc-mingw-w64-i686", "gcc-mingw-w64-x86-64"],
        "Wine": ["wine", "winetricks", "wine32"],
        "Wordlists": ["wordlists"],
        "FreeRDP": ["freerdp2-x11"],
        "xprobe": ["xprobe"],
        "p0f": ["p0f"],
        "gdp-peda": ["gdb-peda"],
        "nbtscan": ["nbtscan"],
        "Apache, PHP, and MySQL": ["apache2", "php", "php-cli", "php-curl", "libapache2-mod-php", "default-mysql-server", "php-mysql"],
        "sshpass": ["sshpass"],
        "Firmware mod kit": ["firmware-mod-kit"],
        "Sublime Text 3": ["sublime-text"],
        "SSH Server": ["openssh-server"],
        "bridge utils": ["bridge-utils"],
        "Mobile Tools": ["aapt", "abe", "adb", "apktool", "burp", "bytecode-viewer", "enjarify", "file", "gedit", "ideviceinstaller", "smali", "sqlite3"]
    }

    _COMMANDS_BEFORE = {
        "Adding MongoDB repo key": ["wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -"],
        "Adding sublime repo key": ["wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -"],
        "Adding x86 repos": ["dpkg --add-architecture i386"],
    }

    _COMMANDS_AFTER = {
        "Installing ruler": ["GO111MODULE=on GOPATH=/opt/ruler go get github.com/sensepost/ruler", "ln -s /opt/ruler/bin/ruler /usr/local/bin"],
        "Updating IEEE oui list": ["airodump-ng-oui-update"],
        "Adding index to web server": ['echo "It works" > /var/www/html/index.html'],
        "Generating SSH key": ["sudo -E -u {0} ssh-keygen -b 4096 -t rsa -f ~/.ssh/id_rsa -P ''".format(get_user())],
    }

    def check(self, config):
        return True

    def install(self, config):
        print_status("Executing pre-install commands...", 1)
        for title,cmds in self._COMMANDS_BEFORE.items():
            print_status("{0}...".format(title), 2)
            for cmd in cmds:
                run_command(cmd)
            print_success("Done!",2)
        print_success("Done executing pre-install commands", 1)

        print_status("Adding new repositories", 1)
        for name,repo in self._REPOS_TO_ADD.items():
            file_write("/etc/apt/sources.list.d/{0}.list".format(name), repo)

        print_status("Updating repos before starting installs", 1)
        run_command("apt update")

        print_status("Installing packages!", 1)
        for title,pkgs in self._PACKAGES.items():
            print_status("Installing {0}...".format(title), 2)
            apt_install(pkgs)
            print_success("Done!",2)
        print_success("Done installing packages!", 1)

        print_status("Executing post-install commands...", 1)
        for title, cmds in self._COMMANDS_AFTER.items():
            print_status("{0}...".format(title), 2)
            for cmd in cmds:
                run_command(cmd)
            print_success("Done!", 2)
        print_success("Done executing post-install commands", 1)



