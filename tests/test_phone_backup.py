import pytest
import subprocess
from ADBSync.FileSystems.Android import AndroidFileSystem
from phone_backup import ADB, dir_exists_on_phone, DirToBackup, ROOT_SDCARD_2


@pytest.fixture
def fs_android() -> AndroidFileSystem:
    return AndroidFileSystem([str(ADB)], "UTF-8")


def test_empty_line(fs_android: AndroidFileSystem):
    res = list(fs_android.adb_shell([":"]))
    assert len(res) == 0


def test_ls_sdcard(fs_android: AndroidFileSystem):
    res = list(fs_android.adb_shell(["ls", "/sdcard/"]))
    expected_dirs = ('DCIM', 'Download', 'Pictures', 'Android')
    for expected_dir in expected_dirs:
        assert expected_dir in res


def test_subprocess_call():
    res = subprocess.run(f"{ADB} shell ls /sdcard/", shell=True, capture_output=True, encoding="utf-8")
    print(res.stdout.splitlines())


def test_exists_on_phone_1():
    dir_ = DirToBackup(path="Sounds", excludes=(".backup",))
    assert dir_exists_on_phone(dir_)


def test_exists_on_phone_2():
    dir_ = DirToBackup(path="Download", excludes=(".org.chromium*", ".com.google.Chrome*"))
    assert dir_exists_on_phone(dir_)


def test_exists_on_phone_3():
    dir_ = DirToBackup(path="Pictures", excludes=(".Gallery2", ".thumbnails"), root=ROOT_SDCARD_2)
    print(dir_.full_path)
    assert not dir_exists_on_phone(dir_)


@pytest.mark.skip()
def test_ls_with_spaces(fs_android: AndroidFileSystem):
    res = fs_android.adb_shell(["ls", "/sdcard/Download"])
    assert "Adobe\\ Reader" in list(res)
 

def test_escape_path(fs_android: AndroidFileSystem):
    path = "/sdcard/Download/Adobe Reader"
    assert fs_android.escape_path(path) == "'/sdcard/Download/Adobe\\ Reader'"
