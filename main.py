import sys
import os
import threading
import time

os.environ.setdefault("CUSTOMTKINTER_DPI_AWARENESS", "1")

from monitor import Monitor
from ui import PulseWindow
from tray import Tray
from autostart import is_autostart_enabled, enable_autostart


class PulseApp:
    def __init__(self):
        self.monitor = Monitor()
        self.window = None
        self.tray = None
        self._running = True
        self._window_visible = False

    def run(self):
        self.window = PulseWindow()
        self.window.withdraw()
        self._window_visible = False

        if not is_autostart_enabled():
            enable_autostart()

        self.tray = Tray(on_show=self.show_window, on_quit=self.quit)
        self.tray.start()

        updater = threading.Thread(target=self._update_loop, daemon=True)
        updater.start()

        self.window.after(100, self.show_window)

        try:
            self.window.protocol("WM_DELETE_WINDOW", self.hide_window)
            self.window.mainloop()
        finally:
            self._running = False
            self.tray.stop()

    def show_window(self, *_):
        if not self._window_visible:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            self._window_visible = True

    def hide_window(self):
        self.window.withdraw()
        self._window_visible = False

    def quit(self, *_):
        self._running = False
        self.window.after(0, self.window.destroy)

    def _update_loop(self):
        while self._running:
            try:
                info = self.monitor.sample()
                self.window.after(0, self._apply_info, info)
                tooltip = (
                    f"Pulse\n"
                    f"CPU: {info.cpu_percent:.0f}%  "
                    f"RAM: {info.ram_percent:.0f}%"
                )
                self.tray.update_tooltip(tooltip)
            except Exception as e:
                print(f"Update error: {e}", file=sys.stderr)
            time.sleep(1.5)

    def _apply_info(self, info):
        try:
            self.window.update_info(info)
        except Exception as e:
            print(f"UI update error: {e}", file=sys.stderr)


def main():
    try:
        import ctypes
        mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "PulseAppMutex_v1")
        if ctypes.windll.kernel32.GetLastError() == 183:
            sys.exit(0)
    except Exception:
        pass

    app = PulseApp()
    app.run()


if __name__ == "__main__":
    main()