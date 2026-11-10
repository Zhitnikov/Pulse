import sys
import winreg


AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "Pulse"


def get_exe_path() -> str:
    if getattr(sys, 'frozen', False):
        return sys.executable
    return sys.argv[0]


def is_autostart_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY)
        try:
            winreg.QueryValueEx(key, APP_NAME)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def enable_autostart():
    exe_path = get_exe_path()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"Failed to enable autostart: {e}")


def disable_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, APP_NAME)
        finally:
            winreg.CloseKey(key)
    except Exception as e:
        print(f"Failed to disable autostart: {e}")