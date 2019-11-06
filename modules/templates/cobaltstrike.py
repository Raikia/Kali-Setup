#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _DOWNLOAD_LINK = None
    _LICENSE = None

    _SCRIPTS = [
        'killswitch-GUI/CobaltStrike-ToolKit',
        'kussic/CS-KickassBot',
        'ZonkSec/persistence-aggressor-script',
        'harleyQu1nn/AggressorScripts',
        'ramen0x3f/AggressorScripts',
    ]

    def check(self, config):
        if config.get('cobaltstrike', 'license', fallback="") == "":
            return "Missing license!"
        post_data = "dlkey={0}".format(config.get('cobaltstrike', 'license'))
        license_link = run_command_with_output("curl -s --data {0} 'https://cobaltstrike.com/download' | grep -m 1 -oP '(downloads/[a-z0-9]{{32}}/cobaltstrike-trial)'".format(escape(post_data)), safe=True).rstrip()
        if license_link == "":
            return "Invalid Cobalt Strike License!"
        self._DOWNLOAD_LINK = "https://cobaltstrike.com/{0}.tgz".format(license_link)
        self._LICENSE = config.get('cobaltstrike', 'license')
        return True

    def install(self, config):
        print_status("Installing Java...", 1)
        apt_install("default-jre")
        print_status("Java installed!", 1)
        print_status("Downloading cobaltstrike", 1)
        file_download(self._DOWNLOAD_LINK, "/root/cobaltstrike.tgz")
        print_status("Decompressing cobaltstrike", 1)
        run_command("tar -zxf /root/cobaltstrike.tgz -C /opt/")
        run_command("/root/cobaltstrike.tgz")
        file_write("/root/.cobaltstrike.license", self._LICENSE)
        print_status("Updating cobaltstrike to licensed version", 1)
        run_command("cd /opt/cobaltstrike/; ./update")
        print_success("Done installing cobaltstrike!", 1)
        
        print_status("Installing some useful scripts", 1)
        make_dir("/opt/cobaltstrike_scripts")
        for repo in _SCRIPTS:
            github_clone(repo, "/opt/cobaltstrike_scripts")
        run_command("ln -sf /opt/cobaltstrike_scripts/ /opt/cobaltstrike/scripts")
        print_success("CobaltStrike Scripts installed to /opt/cobaltstrike_scripts/", 1)