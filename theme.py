LIGHT = {
    "bg": "#F2F2F7",
    "card": "#FFFFFF",
    "text": "#1C1C1E",
    "text_secondary": "#8E8E93",
    "separator": "#C6C6C8",
    "accent": "#007AFF",
    "green": "#34C759",
    "yellow": "#FFCC00",
    "orange": "#FF9500",
    "red": "#FF3B30",
    "purple": "#AF52DE",
}

DARK = {
    "bg": "#000000",
    "card": "#1C1C1E",
    "text": "#FFFFFF",
    "text_secondary": "#8E8E93",
    "separator": "#38383A",
    "accent": "#0A84FF",
    "green": "#30D158",
    "yellow": "#FFD60A",
    "orange": "#FF9F0A",
    "red": "#FF453A",
    "purple": "#BF5AF2",
}


def get_theme(mode: str = "system") -> dict:
    if mode == "light":
        return LIGHT
    if mode == "dark":
        return DARK
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return LIGHT if value == 1 else DARK
    except Exception:
        return LIGHT