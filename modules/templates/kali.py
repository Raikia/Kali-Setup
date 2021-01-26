#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    def check(self, config):
        return True

    def install(self, config):
        if config.getboolean('kali', 'bleeding edge repos', fallback=False):
            print_status("Enabling the bleeding edge repositories", 1)
            file_write("/etc/apt/sources.list.d/kali-bleeding.list", "deb http://http.kali.org/kali kali-bleeding-edge contrib non-free main")
            print_status("Updating and upgrading to bleeding edge repos", 1)
            run_command("apt -qq -y update")
            run_command("DEBIAN_FRONTEND='noninteractive' apt-get -y -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' dist-upgrade --fix-missing")
        print_status("Installing full Kali", 1)
        apt_install('kali-linux-large')
        print_success("Done!", 1)

        print_status("Setting audio level to 0", 1)
        run_command("systemctl --user enable pulseaudio", as_user=True)
        run_command("systemctl --user start pulseaudio", as_user=True)
        run_command("pactl set-sink-mute 0 0", as_user=True)
        run_command("pactl set-sink-volume 0 25%", as_user=True)
        print_success("Done!", 1)

        print_status("Setting grub boot timeout to 1 second", 1)
        file_backup('/etc/default/grub')
        file_replace('/etc/default/grub', '^GRUB_TIMEOUT=.*', "GRUB_TIMEOUT=1")
        file_replace('/etc/default/grub', '^GRUB_CMDLINE_LINUX_DEFAULT=.*', 'GRUB_CMDLINE_LINUX_DEFAULT="vga=0x0318"')
        run_command('update-grub')
        print_success("Done!", 1)

        print_status("Configuring user home folders", 1)
        run_command('find ~/ -maxdepth 1 -mindepth 1 -type d \( -name "Documents" -o -name "Music" -o -name "Pictures" -o -name "Public" -o -name "Templates" -o -name "Videos" \) -empty -delete')
        apt_install('xdg-user-dirs')
        run_command('xdg-user-dirs-update')
        run_command('rm -f {0}/.cache/sessions/*'.format(get_home_folder()))
        print_success("Done", 1)

        print_status("Disabling screensaver", 1)
        run_command("xset s 0 0", as_user=True)
        run_command("xset s off", as_user=True)
        file_append_once('{0}/.xinitrc'.format(get_home_folder()), "xset s off")
        file_append_once('{0}/.xinitrc'.format(get_home_folder()), "xset b off")
        if command_exists('gsettings'):
            run_command('gsettings set org.gnome.desktop.session idle-delay 0')
        print_success("Done!", 1)

        print_status("Allowing root SSH login", 1)
        file_replace('/etc/ssh/sshd_config', '^.*PermitRootLogin .*', 'PermitRootLogin yes')
        print_success("Done!", 1)
