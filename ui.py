import customtkinter as ctk
from monitor import SystemInfo, format_uptime, format_time
from theme import get_theme


class PulseWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.theme = get_theme("system")
        self._apply_theme()

        self.title("Pulse")
        self.geometry("1100x580")
        self.minsize(900, 560)
        self.resizable(True, True)

        self.attributes('-alpha', 0.88)

        self.container = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg"],
            corner_radius=0
        )
        self.container.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_header()

        self.cards_frame = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )
        self.cards_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.cpu_card = self._make_card("Процессор")
        self.gpu_card = self._make_card("Графика")
        self.ram_card = self._make_card("Память")
        self.disk_card = self._make_card("Накопитель")
        self.net_card = self._make_card("Сеть")
        self.battery_card = self._make_card("Питание")

        self._labels = {}
        self._bars = {}

        self._populate()
        self._arrange_cards()

    def _apply_theme(self):
        ctk.set_appearance_mode("dark" if self.theme["bg"] == "#000000" else "light")
        ctk.set_default_color_theme("blue")

    def _build_header(self):
        header = ctk.CTkFrame(
            self.container,
            fg_color="transparent",
            corner_radius=0,
            height=70
        )
        header.pack(fill="x", padx=0, pady=(12, 0))
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="Pulse",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=self.theme["text"]
        )
        title.pack(anchor="w", padx=20, pady=(8, 0))

        subtitle = ctk.CTkLabel(
            header,
            text="Состояние системы",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.theme["text_secondary"]
        )
        subtitle.pack(anchor="w", padx=20)

    def _make_card(self, title: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self.cards_frame,
            fg_color=self.theme["card"],
            corner_radius=16,
            border_width=1,
            border_color=self.theme["separator"]
        )

        header = ctk.CTkLabel(
            card,
            text=title.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.theme["text_secondary"]
        )
        header.pack(anchor="w", padx=16, pady=(12, 2))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        card._content = content
        return card

    def _add_row(self, card: ctk.CTkFrame, label: str, key: str, big: bool = False):
        row = ctk.CTkFrame(card._content, fg_color="transparent")
        row.pack(fill="x", pady=1)

        left = ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.theme["text_secondary"]
        )
        left.pack(side="left")

        size = 22 if big else 15
        weight = "bold" if big else "normal"
        right = ctk.CTkLabel(
            row,
            text="—",
            font=ctk.CTkFont(family="Segoe UI", size=size, weight=weight),
            text_color=self.theme["text"]
        )
        right.pack(side="right")

        self._labels[key] = right
        return right

    def _add_bar(self, card: ctk.CTkFrame, key: str, color: str = None):
        bar_frame = ctk.CTkFrame(card._content, fg_color="transparent")
        bar_frame.pack(fill="x", pady=(4, 2))

        bar = ctk.CTkProgressBar(
            bar_frame,
            height=6,
            corner_radius=3,
            fg_color=self.theme["separator"],
            progress_color=color or self.theme["accent"]
        )
        bar.pack(fill="x")
        bar.set(0)
        self._bars[key] = bar

    def _populate(self):
        self._add_row(self.cpu_card, "Модель", "cpu_name")
        self._add_row(self.cpu_card, "Ядра / Потоки", "cpu_cores")
        self._add_row(self.cpu_card, "Частота", "cpu_freq")
        self._add_row(self.cpu_card, "Температура", "cpu_temp")
        self._add_row(self.cpu_card, "Загрузка", "cpu_percent", big=True)
        self._add_bar(self.cpu_card, "cpu_bar", self.theme["orange"])

        self._add_row(self.gpu_card, "Модель", "gpu_name")
        self._add_row(self.gpu_card, "Температура", "gpu_temp")
        self._add_row(self.gpu_card, "Загрузка", "gpu_percent", big=True)
        self._add_bar(self.gpu_card, "gpu_bar", self.theme["purple"])

        self._add_row(self.ram_card, "Использовано", "ram_used", big=True)
        self._add_bar(self.ram_card, "ram_bar", self.theme["accent"])
        self._add_row(self.ram_card, "Доступно", "ram_available")
        self._add_row(self.ram_card, "Swap", "swap_used")
        self._add_row(self.ram_card, "Процессы", "process_count")

        self._add_row(self.disk_card, "Занято", "disk_used", big=True)
        self._add_bar(self.disk_card, "disk_bar", self.theme["green"])
        self._add_row(self.disk_card, "Чтение", "disk_read")
        self._add_row(self.disk_card, "Запись", "disk_write")

        self._add_row(self.net_card, "IP", "local_ip")
        self._add_row(self.net_card, "Загрузка", "net_down", big=True)
        self._add_row(self.net_card, "Отдача", "net_up")

        self._add_row(self.battery_card, "Заряд", "battery_percent", big=True)
        self._add_bar(self.battery_card, "battery_bar", self.theme["green"])
        self._add_row(self.battery_card, "Состояние", "battery_state")
        self._add_row(self.battery_card, "Осталось", "battery_time")
        self._add_row(self.battery_card, "Аптайм", "uptime")

    def _arrange_cards(self):
        cards = [
            self.cpu_card,
            self.gpu_card,
            self.ram_card,
            self.disk_card,
            self.net_card,
            self.battery_card
        ]

        row = 0
        col = 0
        for card in cards:
            card.grid(row=row, column=col, padx=(0, 8), pady=(0, 8), sticky="nsew")
            col += 1
            if col >= 3:
                col = 0
                row += 1

        self.cards_frame.grid_columnconfigure(0, weight=1)
        self.cards_frame.grid_columnconfigure(1, weight=1)
        self.cards_frame.grid_columnconfigure(2, weight=1)

    def update_info(self, info: SystemInfo):
        def set_text(key, text):
            if key in self._labels:
                self._labels[key].configure(text=text)

        def set_bar(key, value):
            if key in self._bars:
                self._bars[key].set(max(0, min(1, value)))

        cpu_name = info.cpu_name
        if len(cpu_name) > 38:
            cpu_name = cpu_name[:35] + "…"
        set_text("cpu_name", cpu_name)
        set_text("cpu_cores", f"{info.cpu_cores} / {info.cpu_threads}")
        set_text("cpu_freq", f"{info.cpu_freq:.0f} МГц" if info.cpu_freq else "—")
        set_text("cpu_temp", f"{info.cpu_temp:.0f} °C" if info.cpu_temp else "—")
        set_text("cpu_percent", f"{info.cpu_percent:.0f}%")
        set_bar("cpu_bar", info.cpu_percent / 100)

        gpu_name = info.gpu_name or "—"
        if len(gpu_name) > 38:
            gpu_name = gpu_name[:35] + "…"
        set_text("gpu_name", gpu_name)
        set_text("gpu_temp", f"{info.gpu_temp:.0f} °C" if info.gpu_temp else "—")
        set_text("gpu_percent", f"{info.gpu_percent:.0f}%" if info.gpu_name else "—")
        set_bar("gpu_bar", info.gpu_percent / 100)

        set_text("ram_used", f"{info.ram_used_gb:.1f} / {info.ram_total_gb:.1f} ГБ")
        set_bar("ram_bar", info.ram_percent / 100)
        set_text("ram_available", f"{info.ram_available_gb:.1f} ГБ")
        set_text("swap_used", f"{info.swap_used_gb:.1f} / {info.swap_total_gb:.1f} ГБ")
        set_text("process_count", str(info.process_count))

        set_text("disk_used", f"{info.disk_used_gb:.0f} / {info.disk_total_gb:.0f} ГБ")
        set_bar("disk_bar", info.disk_percent / 100)
        set_text("disk_read", f"{info.disk_read_mb_s:.1f} МБ/с")
        set_text("disk_write", f"{info.disk_write_mb_s:.1f} МБ/с")

        set_text("local_ip", info.local_ip)
        set_text("net_down", f"↓ {info.net_download_mb_s:.2f} МБ/с")
        set_text("net_up", f"↑ {info.net_upload_mb_s:.2f} МБ/с")

        if info.battery_percent is not None:
            set_text("battery_percent", f"{info.battery_percent:.0f}%")
            set_bar("battery_bar", info.battery_percent / 100)
            state = "Заряжается" if info.battery_plugged else "Работает от батареи"
            set_text("battery_state", state)
            set_text("battery_time", format_time(info.battery_time_left))
            set_text("uptime", format_uptime(info.uptime_seconds))