#!/usr/bin/env python3

from modules.common.automation import *

class InstallerTemplate:

    _REPOS = [
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
        'Raikia/Misc-scripts',
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
        'evilmog/ntlmv1-multi',
        'dirkjanm/PrivExchange',
        'rvrsh3ll/FindFrontableDomains',
        'trustedsec/egressbuster',
        'HarmJ0y/TrustVisualizer',
        'aboul3la/Sublist3r',
        'microsoft/ProcDump-for-Linux',
        'GreatSCT/GreatSCT',
        'AlessandroZ/LaZagne',
        'b-mueller/apkx',
        'nccgroup/demiguise',
        'gnuradio/gnuradio',
        'johndekroon/serializekiller',
        'frohoff/ysoserial',
        'enjoiz/XXEinjector',
        'SpiderLabs/HostHunter',
        'smicallef/spiderfoot',
        'rofl0r/proxychains-ng',
        'scipag/vulscan',
    ]

    _ADDITIONAL_INSTRUCTIONS = {
        'Raikia/CredNinja': ['ln -s /opt/raikia_credninja-git/CredNinja.py /usr/local/bin/credninja'],
        'PowerShellEmpire/Empire': ['export STAGING_KEY=random; cd ./setup; bash ./install.sh'],
        'ChrisTruncer/EyeWitness': ['cd ./Python/setup/; bash ./setup.sh'],
        'HarmJ0y/TrustVisualizer': ['apt install -y python3-pip', 'pip install networkx'],
        'Raikia/Misc-scripts': ['ln -s /opt/raikia_misc-scripts-git/np.py /usr/local/bin/np'],
        'rofl0r/proxychains-ng': [
            'cd /opt/rofl0r_proxychains-ng-git/; git pull -q', 
            'cd /opt/rofl0r_proxychains-ng-git/; make -s clean',
            'cd /opt/rofl0r_proxychains-ng-git/; ./configure --prefix=/usr --sysconfdir=/etc',
            'cd /opt/rofl0r_proxychains-ng-git/; make -s',
            'cd /opt/rofl0r_proxychains-ng-git/; make -s install',
            'ln -sf /usr/bin/proxychains4 /usr/local/bin/proxychains-ng'
        ],
        'scipag/vulscan': ['ln -s /opt/scipag_vulscan-git /usr/share/nmap/scripts/vulnscan']
    }

    def check(self, config):
        return True if command_exists("git") else "'git' package not installed"

    def install(self, config):
        print_status("Installing various github tools into /opt", 1)
        for proj in self._REPOS:
            print_status("Cloning {0}...".format(proj), 2)
            github_clone(proj, "/opt/")
            folder_name = "/opt/{0}-git".format(proj.replace('/','_').lower())
            run_command("cd {0}; git pull -q".format(folder_name))
            if proj in self._ADDITIONAL_INSTRUCTIONS:
                for instr in self._ADDITIONAL_INSTRUCTIONS[proj]:
                    run_command("cd {0}; {1}".format(folder_name, instr))
            print_success("Done!", 2)
        print_success("Done installing github tools!", 1)
        
        print_status("Writing GitHub update script", 1)
        update_file_contents = """#!/bin/bash
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
done"""
        file_write('/opt/UpdateAll.sh', update_file_contents)
        run_command('chmod +x /opt/UpdateAll.sh')
        print_success('Done', 1)
