import pystray
from icon import create_tray_icon
from autostart import is_autostart_enabled, enable_autostart, disable_autostart


class Tray:
    def __init__(self, on_show, on_quit):
        self._on_show = on_show
        self._on_quit = on_quit
        self._icon = None
        self._autostart_enabled = is_autostart_enabled()

    def _toggle_autostart(self):
        if self._autostart_enabled:
            disable_autostart()
            self._autostart_enabled = False
        else:
            enable_autostart()
            self._autostart_enabled = True
        self._update_menu()

    def _update_menu(self):
        if self._icon:
            self._icon.menu = self._make_menu()

    def _make_menu(self):
        autostart_item = pystray.MenuItem(
            "Автозапуск",
            self._toggle_autostart,
            checked=lambda item: self._autostart_enabled
        )
        return pystray.Menu(
            pystray.MenuItem("Открыть Pulse", self._on_show, default=True),
            pystray.Menu.SEPARATOR,
            autostart_item,
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", self._on_quit),
        )

    def start(self):
        image = create_tray_icon()
        self._icon = pystray.Icon(
            name="pulse",
            icon=image,
            title="Pulse",
            menu=self._make_menu()
        )
        self._icon.run_detached()

    def stop(self):
        if self._icon:
            self._icon.stop()

    def update_tooltip(self, text: str):
        if self._icon:
            self._icon.title = text