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
        self.load_download_link(config)
        if self._DOWNLOAD_LINK is None:
            return "Invalid Cobalt Strike License!"
        return True

    def install(self, config):
        print_status("Installing Java...", 1)
        apt_install("default-jre")
        print_status("Java installed!", 1)
        print_status("Downloading cobaltstrike", 1)
        self.load_download_link(config)
        if self._DOWNLOAD_LINK is None:
            print_error("CobaltStrike license is invalid now!", 1)
            return
        file_download(self._DOWNLOAD_LINK, "{0}/cobaltstrike.tgz".format(get_home_folder()))
        print_status("Decompressing cobaltstrike", 1)
        run_command("tar -zxf {0}/cobaltstrike.tgz -C /opt/".format(get_home_folder()))
        run_command("rm {0}/cobaltstrike.tgz".format(get_home_folder()))
        file_write("{0}/.cobaltstrike.license".format(get_home_folder()), self._LICENSE)
        file_write("/root/.cobaltstrike.license", self._LICENSE)
        print_status("Updating cobaltstrike to licensed version", 1)
        run_command("cd /opt/cobaltstrike/; ./update")
        print_success("Done installing cobaltstrike!", 1)
        
        print_status("Installing some useful scripts", 1)
        make_dir("/opt/cobaltstrike_scripts")
        for repo in self._SCRIPTS:
            github_clone(repo, "/opt/cobaltstrike_scripts")
        run_command("ln -sf /opt/cobaltstrike_scripts/ /opt/cobaltstrike/scripts")
        print_success("CobaltStrike Scripts installed to /opt/cobaltstrike_scripts/", 1)


    def load_download_link(self, config):
        post_data = "dlkey={0}".format(config.get('cobaltstrike', 'license'))
        license_link = run_command_with_output("curl -s --data {0} 'https://cobaltstrike.com/download' | grep -m 1 -oP '(downloads/[a-z0-9]{{32}}/cobaltstrike-dist)'".format(escape(post_data)), safe=True).rstrip()
        if license_link != "":
            self._DOWNLOAD_LINK = "https://cobaltstrike.com/{0}.tgz".format(license_link)
            self._LICENSE = config.get('cobaltstrike', 'license')
        else:
            self._DOWNLOAD_LINK = None
            self._LICENSE = None
