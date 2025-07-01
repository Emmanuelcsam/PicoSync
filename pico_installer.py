#!/usr/bin/env python3
"""
PicoSync Universal Installer
Cross-platform installer for PicoSync that works on both Windows and Linux
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class PicoInstaller:
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.python_cmd = sys.executable
        
    def check_python(self):
        """Check if Python is properly installed"""
        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro} detected")
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            print("ERROR: Python 3.6 or higher is required")
            return False
        return True
        
    def install_dependencies(self):
        """Install required Python packages"""
        print("\nInstalling dependencies...")
        try:
            subprocess.check_call([self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call([self.python_cmd, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install dependencies: {e}")
            return False
            
    def create_launcher(self):
        """Create platform-specific launcher"""
        if self.is_windows:
            self.create_windows_launcher()
        elif self.is_linux:
            self.create_linux_launcher()
            
    def create_windows_launcher(self):
        """Create Windows batch file launcher"""
        launcher_content = f'''@echo off
"{self.python_cmd}" "%~dp0pico_sync_manager.py" %*
if errorlevel 1 pause
'''
        with open("PicoSync.bat", "w") as f:
            f.write(launcher_content)
        print("Created PicoSync.bat launcher")
        
    def create_linux_launcher(self):
        """Create Linux shell script launcher"""
        launcher_content = f'''#!/bin/bash
cd "$(dirname "$0")"
{self.python_cmd} pico_sync_manager.py "$@"
'''
        launcher_path = Path("PicoSync.sh")
        with open(launcher_path, "w") as f:
            f.write(launcher_content)
        launcher_path.chmod(0o755)
        print("Created PicoSync.sh launcher")
        
    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        if self.is_windows:
            self.create_windows_shortcut()
        elif self.is_linux:
            self.create_linux_desktop_entry()
            
    def create_windows_shortcut(self):
        """Create Windows desktop shortcut"""
        try:
            import win32com.client
            desktop = Path.home() / "Desktop"
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(desktop / "PicoSync.lnk"))
            shortcut.Targetpath = str(Path.cwd() / "PicoSync.bat")
            shortcut.WorkingDirectory = str(Path.cwd())
            shortcut.IconLocation = sys.executable
            shortcut.save()
            print("Created desktop shortcut")
        except ImportError:
            print("Note: Install pywin32 to create desktop shortcuts")
            
    def create_linux_desktop_entry(self):
        """Create Linux desktop entry"""
        desktop_entry = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=PicoSync
Comment=Raspberry Pi Pico Sync Manager
Exec={Path.cwd()}/PicoSync.sh
Icon=applications-development
Terminal=false
Categories=Development;
'''
        desktop_path = Path.home() / ".local/share/applications"
        desktop_path.mkdir(parents=True, exist_ok=True)
        
        with open(desktop_path / "picosync.desktop", "w") as f:
            f.write(desktop_entry)
        print("Created desktop entry")
        
    def check_permissions(self):
        """Check and fix permissions for Linux"""
        if self.is_linux:
            print("\nChecking USB permissions...")
            groups = subprocess.getoutput("groups")
            if "dialout" not in groups:
                print("WARNING: You may need to add your user to the 'dialout' group:")
                print(f"  sudo usermod -a -G dialout {os.getlogin()}")
                print("  Then log out and back in for changes to take effect")
                
    def run(self):
        """Run the installer"""
        print("=== PicoSync Universal Installer ===")
        print(f"Platform: {self.system}")
        
        if not self.check_python():
            return False
            
        if not self.install_dependencies():
            return False
            
        self.create_launcher()
        self.create_desktop_shortcut()
        self.check_permissions()
        
        print("\n=== Installation Complete! ===")
        if self.is_windows:
            print("Run PicoSync.bat to start the application")
        else:
            print("Run ./PicoSync.sh to start the application")
            
        return True

if __name__ == "__main__":
    installer = PicoInstaller()
    success = installer.run()
    if not success:
        sys.exit(1)