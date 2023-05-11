#-*- coding:utf-8 -*-
"""
Usage:
PHONE_BACKUP_SSH_HOST="my-ssh-server" python3 -u rsync_to_remote.py

The remote ssh server access is expected to be configured in ~/.ssh/config, for instance:
Host my-ssh-server
  IdentityFile /path/to/password-protected/ssh/private/key
  User my-user
"""

import sys
from os import getenv
from subprocess import call
from pathlib import Path


def get_ssh_host() -> str:
    PHONE_BACKUP_SSH_HOST = getenv("PHONE_BACKUP_SSH_HOST")
    if PHONE_BACKUP_SSH_HOST is None:
        sys.exit("Error: PHONE_BACKUP_SSH_HOST is not set")
    return PHONE_BACKUP_SSH_HOST


def main():
    ssh_host = get_ssh_host()
    src = Path.home() / "phone_backup"
    dst = f"~/phone_backup"
    call(f"/usr/bin/rsync -avz --progress {src}/ {ssh_host}:{dst}/", shell=True)


if __name__ == "__main__":
    main()
