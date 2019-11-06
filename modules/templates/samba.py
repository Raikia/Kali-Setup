#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _CONFIG = """
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


    def check(self, config):
        return True

    def install(self, config):
        print_status("Installing samba", 1)
        apt_install('samba cifs-utils')
        print_success("Done!", 1)

        print_status("Configuring samba", 1)
        run_command("groupdel smbgroup")
        run_command("groupadd smbgroup")
        run_command("userdel samba")
        run_command("useradd -r -M -d /nonexistent -s /bin/false -c 'Samba User' -g smbgroup samba")
        file_backup('/etc/samba/smb.conf')
        if not file_contains('/etc/samba/smb.conf', '[shared]'):
            file_append('/etc/samba/smb.conf', self._CONFIG)
        make_dir('/var/samba/')
        run_command('chown -R samba:smbgroup /var/samba/')
        run_command('chmod -R 0755 /var/samba/')
        run_command('touch /etc/printcap')
        run_command('systemctl stop samba')
        run_command('systemctl disable samba')
        print_success("Done!", 1)
