import psutil
import platform
import subprocess
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class SystemInfo:
    cpu_name: str = ""
    cpu_percent: float = 0.0
    cpu_freq: float = 0.0
    cpu_temp: Optional[float] = None
    cpu_cores: int = 0
    cpu_threads: int = 0

    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    ram_percent: float = 0.0

    swap_used_gb: float = 0.0
    swap_total_gb: float = 0.0

    process_count: int = 0

    gpu_name: str = ""
    gpu_percent: float = 0.0
    gpu_temp: Optional[float] = None

    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_read_mb_s: float = 0.0
    disk_write_mb_s: float = 0.0

    net_download_mb_s: float = 0.0
    net_upload_mb_s: float = 0.0
    local_ip: str = ""

    battery_percent: Optional[float] = None
    battery_plugged: bool = False
    battery_time_left: Optional[float] = None

    os_name: str = ""
    hostname: str = ""
    uptime_seconds: float = 0.0


class Monitor:
    def __init__(self):
        self._last_disk = psutil.disk_io_counters()
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()
        self._cpu_name = self._get_cpu_name()
        self._gpu_info = self._get_gpu_info()

    def _get_cpu_name(self) -> str:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            )
            name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            winreg.CloseKey(key)
            return name.strip()
        except Exception:
            return platform.processor() or "Unknown CPU"

    def _get_gpu_info(self) -> dict:
        info = {"name": "", "method": None}
        try:
            out = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=2
            )
            info["name"] = out.strip()
            info["method"] = "nvidia"
            return info
        except Exception:
            pass

        try:
            import wmi
            c = wmi.WMI()
            for gpu in c.Win32_VideoController():
                info["name"] = gpu.Name
                info["method"] = "wmi"
                break
        except Exception:
            pass

        return info

    def _get_cpu_temp(self) -> Optional[float]:
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if entry.current and entry.current > 0:
                            return entry.current
        except Exception:
            pass

        try:
            import wmi
            c = wmi.WMI(namespace="root\\wmi")
            for t in c.MSAcpi_ThermalZoneTemperature():
                kelvin = t.CurrentTemperature / 10.0
                celsius = kelvin - 273.15
                if 0 < celsius < 120:
                    return celsius
        except Exception:
            pass

        try:
            import wmi
            c = wmi.WMI(namespace="root\\cimv2")
            for sensor in c.Win32_PerfFormattedData_Counters_ThermalZoneInformation():
                if hasattr(sensor, 'Temperature') and sensor.Temperature:
                    celsius = (float(sensor.Temperature) - 2732) / 10.0
                    if 0 < celsius < 120:
                        return celsius
        except Exception:
            pass

        try:
            import wmi
            c = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            for sensor in c.Sensor():
                if sensor.SensorType == "Temperature" and "CPU" in sensor.Name:
                    if sensor.Value and 0 < sensor.Value < 120:
                        return sensor.Value
        except Exception:
            pass

        return None

    def _get_gpu_stats(self) -> dict:
        stats = {"percent": 0.0, "temp": None}
        if self._gpu_info.get("method") == "nvidia":
            try:
                out = subprocess.check_output(
                    ["nvidia-smi",
                     "--query-gpu=utilization.gpu,temperature.gpu",
                     "--format=csv,noheader,nounits"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=2
                )
                parts = [p.strip() for p in out.split(",")]
                stats["percent"] = float(parts[0])
                stats["temp"] = float(parts[1])
            except Exception:
                pass
        return stats

    def sample(self) -> SystemInfo:
        now = time.time()
        dt = now - self._last_time
        if dt <= 0:
            dt = 1.0

        info = SystemInfo()

        info.cpu_name = self._cpu_name
        info.cpu_percent = psutil.cpu_percent(interval=0.1)
        freq = psutil.cpu_freq()
        info.cpu_freq = freq.current if freq else 0.0
        info.cpu_temp = self._get_cpu_temp()
        info.cpu_cores = psutil.cpu_count(logical=False) or 0
        info.cpu_threads = psutil.cpu_count(logical=True) or 0

        mem = psutil.virtual_memory()
        info.ram_used_gb = mem.used / (1024 ** 3)
        info.ram_total_gb = mem.total / (1024 ** 3)
        info.ram_available_gb = mem.available / (1024 ** 3)
        info.ram_percent = mem.percent

        swap = psutil.swap_memory()
        info.swap_used_gb = swap.used / (1024 ** 3)
        info.swap_total_gb = swap.total / (1024 ** 3)

        info.process_count = len(psutil.pids())

        info.gpu_name = self._gpu_info.get("name", "")
        gpu_stats = self._get_gpu_stats()
        info.gpu_percent = gpu_stats["percent"]
        info.gpu_temp = gpu_stats["temp"]

        try:
            usage = psutil.disk_usage("/")
        except Exception:
            usage = psutil.disk_usage("C:\\")
        info.disk_used_gb = usage.used / (1024 ** 3)
        info.disk_total_gb = usage.total / (1024 ** 3)
        info.disk_percent = usage.percent

        disk_now = psutil.disk_io_counters()
        if self._last_disk:
            info.disk_read_mb_s = (disk_now.read_bytes - self._last_disk.read_bytes) / dt / (1024 ** 2)
            info.disk_write_mb_s = (disk_now.write_bytes - self._last_disk.write_bytes) / dt / (1024 ** 2)
        self._last_disk = disk_now

        net_now = psutil.net_io_counters()
        if self._last_net:
            info.net_download_mb_s = (net_now.bytes_recv - self._last_net.bytes_recv) / dt / (1024 ** 2)
            info.net_upload_mb_s = (net_now.bytes_sent - self._last_net.bytes_sent) / dt / (1024 ** 2)
        self._last_net = net_now

        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            info.local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            info.local_ip = "—"

        batt = psutil.sensors_battery()
        if batt:
            info.battery_percent = batt.percent
            info.battery_plugged = batt.power_plugged
            if batt.secsleft > 0:
                info.battery_time_left = batt.secsleft

        info.os_name = f"{platform.system()} {platform.release()}"
        info.hostname = platform.node()
        info.uptime_seconds = time.time() - psutil.boot_time()

        self._last_time = now
        return info


def format_uptime(seconds: float) -> str:
    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    parts = []
    if days:
        parts.append(f"{days}д")
    if hours or days:
        parts.append(f"{hours}ч")
    parts.append(f"{minutes}м")
    return " ".join(parts)


def format_time(seconds: Optional[float]) -> str:
    if seconds is None or seconds < 0:
        return "—"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}ч {minutes}м"