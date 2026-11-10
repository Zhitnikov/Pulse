# Pulse

Lightweight Windows system monitor running in the system tray. Displays real-time hardware metrics in a minimalist interface.

## Features

- System tray integration with toggleable auto-start via Windows Registry.
- Real-time metrics:
  - **CPU**: Model, cores/threads, frequency, temperature, usage.
  - **GPU**: Model, temperature, usage.
  - **RAM**: Used, available, swap, active processes.
  - **Disk**: Usage, read/write speeds.
  - **Network**: Local IP, download/upload speeds.
  - **Battery**: Charge level, state, time remaining.
- Single executable file distribution.
- 1.5-second metric update interval.

## Tech Stack

- Python
- `customtkinter` (UI)
- `psutil`, `wmi` (System metrics)
- `pystray` (System tray)
- `PyInstaller` (Build)

## Usage

1. Download `Pulse.exe` from the latest Release.
2. Run the executable.
3. The application starts minimized to the system tray and adds itself to Windows auto-start.
4. Right-click the tray icon to open the window, toggle auto-start, or exit.

## Building from source

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pyinstaller
python build.py
```

The compiled executable is located in the `dist/` directory.

## Notes

- CPU temperature relies on `psutil` or WMI thermal zones. If temperatures do not display, running a background tool like LibreHardwareMonitor may be required for WMI exposure.
- GPU metrics are fetched via `nvidia-smi` for NVIDIA GPUs. AMD/Intel GPUs only display the model name via WMI.