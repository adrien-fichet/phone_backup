#-*- coding:utf-8 -*-

from subprocess import call
from pathlib import Path
from vars import (
    SSH_USER,
    SSH_PASSWORD_FILE,  # a Path object to the ssh password file
    SSH_HOST
)


def main():
    src = Path.home() / "phone_backup"
    dst = f"/home/{SSH_USER}/phone_backup"
    password = SSH_PASSWORD_FILE.read_text()
    call(f"sshpass -p {password} /usr/bin/rsync -avz --progress {src}/ {SSH_USER}@{SSH_HOST}:{dst}/", shell=True)


if __name__ == "__main__":
    main()
