import sys
import os
import win32com.client
from pathlib import Path

def create_shortcut(shortcut_path_str, target_path_str, working_dir_str, icon_path_str):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path_str)
    shortcut.TargetPath = target_path_str
    shortcut.WorkingDirectory = working_dir_str
    if icon_path_str and Path(icon_path_str).exists():
        shortcut.IconLocation = icon_path_str
    shortcut.save()

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python create_shortcut_windows.py <shortcut_path> <target_path> <working_dir> <run_icon_path> <install_icon_path>")
        sys.exit(1)
    
    shortcut_path = sys.argv[1]
    target_path = sys.argv[2]
    working_dir = sys.argv[3]
    run_icon_path = sys.argv[4]
    install_icon_path = sys.argv[5]
    
    create_shortcut(shortcut_path, target_path, working_dir, run_icon_path)
    # Also create a shortcut for the installer
    install_shortcut_path = str(Path(shortcut_path).parent / "PicoSync Installer.lnk")
    install_target_path = str(Path(target_path).parent.parent / "install_picosync.bat")
    create_shortcut(install_shortcut_path, install_target_path, working_dir, install_icon_path)
