#-*- coding:utf-8 -*-
"""
- ADB documentation: https://developer.android.com/studio/command-line/adb
- Download the Android platform tools from: https://developer.android.com/studio/releases/platform-tools
- Ensure that USB debugging is enabled on the phone (in developer options)
- Authorize the USB debugging on the phone when calling ADB for the first time
- ADBSync repo: https://github.com/jb2170/better-adb-sync
"""

import sys
import ADBSync
from pathlib import Path
from subprocess import check_output


ADB = Path.home() / "Documents" / "platform-tools" / "adb"


def log(msg: str):
    print(f"--> {msg}")


def backup_directory(phone_serial: str) -> Path:
    backup_dir = Path.home() / "phone_backup" / phone_serial
    Path.mkdir(backup_dir, exist_ok=True)
    log(f"Using backup directory {backup_dir}")
    return backup_dir


def get_serial_of_connected_device() -> str:
    log("Listing devices")
    output = check_output(f"'{ADB}' devices -l", shell=True).decode()
    print(output.replace("\n\n", "\n"), end="")

    phone_serial = None
    for line in output.split("\n"):
        if "device usb" in line:
            phone_serial = line.split()[0]

    if phone_serial is None:
        raise Exception("Error: no device found")

    if "unauthorized" in output:
        raise Exception("Error: device unauthorized")

    log(f"Using phone serial {phone_serial}")
    return phone_serial


def main():
    phone_serial = get_serial_of_connected_device() 
    backup_dir = backup_directory(phone_serial)

    dirs_to_backup: tuple[DirToBackup, ...] = (
        DirToBackup(path="Movies", excludes=(".thumbnails", "VideoVolumeBooster")),
        DirToBackup(path="Sounds", excludes=(".backup",)),
        DirToBackup(path="Pictures", excludes=(".Gallery2", ".thumbnails")),
        DirToBackup(path="Download", excludes=(".org.chromium*", ".com.google.Chrome*")),
        DirToBackup(path="DCIM", excludes=(".thumbnails",)),
        DirToBackup(
            path="Android/media/com.whatsapp/Whatsapp", 
            excludes=(".Shared", ".StickerThumbs", ".trash", "Backups", "Databases")
        ),
    )

    sys_argv_original = list(sys.argv)
    for dir_to_backup in dirs_to_backup:
        log(f"Syncing {dir_to_backup.path}")
        adbsync_options = f"--adb-bin {ADB} {dir_to_backup.excludes} -q --show-progress"
        sys.argv.extend(f"{adbsync_options} pull /sdcard/{dir_to_backup.path} {backup_dir}".split())
        ADBSync.main()
        sys.argv = list(sys_argv_original)


class DirToBackup:
    path: str
    _excludes: tuple[str]

    def __init__(self, path: str, excludes: tuple[str, ...] = ()):
        self.path = path
        self._excludes = excludes

    @property
    def excludes(self):
        return " ".join([f"--exclude={exclude}" for exclude in self._excludes])


if __name__ == "__main__":
    main()
