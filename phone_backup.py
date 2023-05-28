#-*- coding:utf-8 -*-
"""
Usage:
python3 -u phone_backup.py

- ADB documentation: https://developer.android.com/studio/command-line/adb
- Download the Android platform tools from: https://developer.android.com/studio/releases/platform-tools
- Ensure that USB debugging is enabled on the phone (in developer options)
- Authorize the USB debugging on the phone when calling ADB for the first time
- ADBSync repo: https://github.com/jb2170/better-adb-sync
"""

import sys
import ADBSync
from pathlib import Path
from subprocess import check_output, CalledProcessError


ADB = Path.home() / "android" / "platform-tools" / "adb"

WHATSAPP_EXCLUDES = (".Shared", ".StickerThumbs", ".trash", "Backups", "Databases", "Media/.Statuses", ".Thumbs")

ROOT_SDCARD_1 = "/sdcard"
ROOT_SDCARD_2 = "/storage/3839-3938"


class DirToBackup:
    path: str
    _excludes: tuple[str]
    root: str

    def __init__(self, path: str, excludes: tuple[str, ...] = (), root: str = ROOT_SDCARD_1):
        self.path = path
        self._excludes = excludes
        self.root = root

    @property
    def excludes(self) -> str:
        return " ".join([f"--exclude={exclude}" for exclude in self._excludes])

    @property
    def full_path(self) -> str:
        return f"{self.root}/{self.path}"


DIRS_TO_BACKUP: tuple[DirToBackup, ...] = (
    DirToBackup(path="Movies", excludes=(".thumbnails", "VideoVolumeBooster")),
    DirToBackup(path="Sounds", excludes=(".backup",)),

    DirToBackup(path="Pictures", excludes=(".Gallery2", ".thumbnails")),
    DirToBackup(path="Pictures", excludes=(".Gallery2", ".thumbnails"), root=ROOT_SDCARD_2),

    DirToBackup(path="Download", excludes=(".org.chromium*", ".com.google.Chrome*")),

    DirToBackup(path="DCIM", excludes=(".thumbnails",)),
    DirToBackup(path="DCIM", excludes=(".thumbnails",), root=ROOT_SDCARD_2),

    DirToBackup(path="Android/media/com.whatsapp/Whatsapp", excludes=WHATSAPP_EXCLUDES),
    DirToBackup(path="WhatsApp", excludes=WHATSAPP_EXCLUDES),
)


def log(msg: str):
    print(f"--> {msg}")


def create_backup_directory(phone_serial: str, dir_to_backup: DirToBackup) -> Path:
    sdcard = 1
    if dir_to_backup.root == ROOT_SDCARD_2:
        sdcard = 2

    backup_dir = Path.home() / "phone_backup" / phone_serial / f"sdcard-{sdcard}"
    Path.mkdir(backup_dir, exist_ok=True, parents=True)
    log(f"Using backup directory {backup_dir}")
    return backup_dir


def get_serial_of_connected_device() -> str:
    log("Listing devices")
    output = check_output(f"'{ADB}' devices -l", shell=True).decode()
    print(output.replace("\n\n", "\n"), end="")

    phone_serial = None
    device_info = ""
    for line in output.split("\n"):
        if "device usb" in line:
            line_split = line.split()
            phone_serial, device_info = line_split[0], " ".join(line_split[1:])

    if phone_serial is None:
        raise Exception("no device found")

    if "unauthorized" in device_info:
        raise Exception("device unauthorized")

    log(f"Using phone serial {phone_serial}")
    return phone_serial


def dir_exists_on_phone(dir_to_backup: DirToBackup) -> bool:
    try:
        check_output(f"'{ADB}' shell ls -d {dir_to_backup.full_path}", shell=True)
    except CalledProcessError:
        return False
    return True


def backup_phone_dir(phone_serial: str, dir_to_backup: DirToBackup):
    if not dir_exists_on_phone(dir_to_backup):
        log(f"The following directory does not exist on this phone, skipping it: {dir_to_backup.full_path}")
        return

    backup_dir = create_backup_directory(phone_serial, dir_to_backup)

    log(f"Syncing {dir_to_backup.full_path} to {backup_dir}")
    adbsync_options = f"--adb-bin {ADB} {dir_to_backup.excludes} -q --show-progress"
    sys.argv.extend(f"{adbsync_options} pull {dir_to_backup.full_path} {backup_dir}".split())
    ADBSync.main()


def main():
    try:
        phone_serial = get_serial_of_connected_device() 
    except Exception as e:
        log(f"Error: {str(e)}, exiting")
        return

    sys_argv_original = list(sys.argv)

    for dir_to_backup in DIRS_TO_BACKUP:
        backup_phone_dir(phone_serial, dir_to_backup) 
        sys.argv = list(sys_argv_original)


if __name__ == "__main__":
    main()
