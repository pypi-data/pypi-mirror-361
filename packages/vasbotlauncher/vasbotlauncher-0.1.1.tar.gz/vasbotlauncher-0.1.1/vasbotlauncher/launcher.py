import sys
import os
import subprocess
import requests

def launch():
    if not sys.version_info >= (3, 12):
        raise RuntimeError("vasbot requires Python 3.12")

    print("[vasbotlauncher] Fetching bot code...")
    url = "https://api.cane.javanodes.in/get_release"
    code = requests.get(url).text

    cwd = os.getcwd()
    bot_file = os.path.join(cwd, "main.py")

    print(f"[vasbotlauncher] Saving main.py to: {cwd}")
    with open(bot_file, "w", encoding="utf-8") as f:
        f.write(code)

    print("[vasbotlauncher] main.py saved.")
    print("[vasbotlauncher] Launching main.py...")

    subprocess.run([sys.executable, "main.py"])
