#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _TYPE = None

    _PACKAGES = {
        "VMware": ["open-vm-tools", "open-vm-tools-desktop"],
        "Virtualbox": ['virtualbox-guest-x11']
    }

    def check(self, config):
        if run_command('dmesg | grep hypervisor | grep -iq vmware', safe=True) == 0:
            self._TYPE = "VMware"
        elif run_command('dmesg | grep hypervisor | grep -iq virtualbox', safe=True) == 0:
            self._TYPE = "Virtualbox"

        if self._TYPE is None:
            return "Not running in a VM"
        return True

    def install(self, config):
        print_status("Installing {0} additions...".format(self._TYPE), 1)
        for cmd in self._PACKAGES[self._TYPE]:
            apt_install(cmd)
        print_success("Done!", 1)

        if self._TYPE == 'VMware':
            print_status("Writing mount shared folders script", 1)
            file_contents = """#!/bin/bash
vmware-hgfsclient | while read folder; do
    echo "[i] Mounting ${folder}    (/mnt/hgfs/${folder})"
    mkdir -p "/mnt/hgfs/${folder}"
    umount -f "/mnt/hgfs/${folder}" 2>/dev/null
    vmhgfs-fuse -o allow_other -o auto_unmount ".host:/${folder}" "/mnt/hgfs/${folder}"
done

sleep 2s
"""
            file_write('/usr/local/sbin/mount-shared-folders', file_contents)
            run_command("chmod +x /usr/local/sbin/mount-shared-folders")
            run_command("ln -sf '/usr/local/sbin/mount-shared-folders' '/root/Desktop/mount-shared-folders.sh'")
            print_success("Done")

        if self._TYPE is not None:
            print_status("Disabling SMART monitoring because we're in a VM")
            run_command("systemctl disable smartmontools.service", show_error=False)
            print_success("Done")
