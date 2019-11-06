#!/usr/bin/env python3

import subprocess
import os
import re
import shlex
from modules.common.printer import *

_VERBOSE = False
_DRY_RUN = False

def automation_set_verbose(ver):
    global _VERBOSE
    _VERBOSE = ver
    if _VERBOSE:
        print_success("VERBOSE is enabled!")

def automation_set_dry_run(sel):
    global _DRY_RUN
    _DRY_RUN = sel
    if _DRY_RUN:
        print_success("DRY RUN is enabled!")

def escape(input):
    return shlex.quote(input)

def apt_install(packages):
    install_packages = []
    if isinstance(packages, (str,)):
        install_packages.append(packages)
    elif isinstance(packages, (list,)):
        install_packages = packages
    else:
        print_error("Unknown thing to install: {0}".format(packages))
        return
    cmd = "export DEBIAN_FRONTEND=noninteractive; apt -y -qq install {0}".format(' '.join(install_packages))
    return run_command(cmd)

def github_clone(repo, dest_folder):
    dest_folder += "/{0}-git".format(repo.replace('/','_').lower())
    cmd = 'git clone --recurse-submodules https://github.com/{0}.git {1}'.format(repo, escape(dest_folder))
    return run_command(cmd)

def file_download(location, destination, safe=False):
    if _DRY_RUN and not safe:
        print_status("Would have downloaded {0} to {1}".format(location, destination), 1)
    else:
        os.system("wget -O '{0}' '{1}' > /dev/null 2>&1".format(destination, location))

def command_exists(cmd):
    return os.system("which {0} > /dev/null 2>&1".format(cmd.split(" ")[0])) == 0

def run_command(cmd, safe=False, print_error=True):
    cmd_run = "{0} {1}".format(cmd, " > /dev/null 2>&1" if not _VERBOSE else "")
    if _DRY_RUN and not safe:
        print_status("Would have run: " + cmd_run, 1)
        ret = 0
    else:
        ret = os.system(cmd_run)
    if ret != 0 and print_error:
        print_error('Failed running "{0}"'.format(cmd_run))
    return ret

def run_command_with_output(cmd, safe=False):
    if _DRY_RUN and not safe:
        print_status("Would have run: " + cmd, 1)
        return ""
    try:
        return subprocess.check_output(cmd, shell=True).decode('ascii')
    except Exception:
        return ""

def make_dir(directory):
    if _DRY_RUN:
        print_status("Would have created directory: " + directory, 1)
        return
    try:
        os.mkdirs(directory)
    except Exception:
        print_error("Unable to make the directory {0}".format(directory))

def file_exists(filename):
    return os.path.exists(filename)

def file_read(filename):
    if not file_exists(filename):
        return ""
    contents = ""
    with open(filename, 'r') as new_file:
        contents = new_file.read().replace('\n',"\n")
    return contents

def file_contains(filename, text):
    return text in file_read(filename)

def file_write(filename, content):
    if _DRY_RUN:
        print_status("Would have written the following to '{0}':\n---------------\n{1}\n---------------\n".format(filename, content))
        return
    with open(filename, 'w') as f:
        f.write(content)

def file_append(filename, content):
    if _DRY_RUN:
        print_status("Would have appended the following to '{0}':\n---------------\n{1}\n---------------\n".format(filename, content))
        return
    with open(filename, 'a') as f:
        f.write("\n"+content)

def file_append_once(filename, content, search=""):
    if search == "":
        search = content
    if not file_contains(filename, search):
        if _DRY_RUN:
            print_status("Would have appended the following to '{0}':\n---------------\n{1}\n---------------\n".format(filename, content))
            return
        file_append(filename, content)

def file_replace(filename, find, replace):
    newText = file_read(filename)
    newText = re.sub(find, replace, newText, flags=re.M)
    file_write(filename, newText)

def file_append_or_replace(filename, find, replace):
    file_replace(filename, find, replace)
    file_append_once(filename, replace)

def file_backup(filename):
    if file_exists(filename):
        new_filename = filename
        while file_exists(new_filename):
            new_filename += ".bkup"
        text = file_read(filename)
        file_write(new_filename, text)