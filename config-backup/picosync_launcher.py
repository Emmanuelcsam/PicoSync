#!/usr/bin/env python3
"""
PicoSync Launcher
Minimal cross‑platform executable that
  1. ensures a local venv exists
  2. installs project requirements with **uv**
  3. runs pico_installer.py
  4. finally starts pico_sync_manager.py

Place this file in the same directory as:
  • pico_installer.py
  • pico_sync_manager.py
  • requirements.txt

Usage:
  $ python picosync_launcher.py
"""

import os
import subprocess
import sys
import platform
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"


def run(cmd: str):
    """Print and run a shell command"""
    print(">>>", cmd)
    subprocess.check_call(cmd, shell=True)


def ensure_venv():
    """Create the virtual environment if it is missing"""
    if VENV.exists():
        return

    run(f"{sys.executable} -m venv "{VENV}"")


def venv_bin(name: str) -> Path:
    """Return absolute path to *name* inside the venv's bin/Scripts folder"""
    b = "Scripts" if platform.system() == "Windows" else "bin"
    return VENV / b / name


def main():
    os.chdir(HERE)
    ensure_venv()

    # Paths inside venv
    python = str(venv_bin("python.exe" if platform.system() == "Windows" else "python"))
    uv = venv_bin("uv.exe" if platform.system() == "Windows" else "uv")

    # Install uv if missing
    if not uv.exists():
        run(f"{python} -m pip install --upgrade pip uv")

    # Install project requirements
    run(f"{uv} pip install -r requirements.txt")

    # Run installer and manager
    run(f"{uv} run python pico_installer.py")
    run(f"{uv} run python pico_sync_manager.py")


if __name__ == "__main__":
    main()
