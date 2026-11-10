import subprocess
import sys
from icon import create_icon

create_icon(256).save("pulse.ico", format="ICO", sizes=[
    (256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)
])

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--noconsole",
    "--onefile",
    "--icon=pulse.ico",
    "--collect-all", "customtkinter",
    "--collect-all", "pystray",
    "--name", "Pulse",
    "main.py"
]

subprocess.check_call(cmd)
print("\nГотово: dist\\Pulse.exe")