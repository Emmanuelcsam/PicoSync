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
import venv
from pathlib import Path

class PicoInstaller:
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.base_dir = Path.cwd()
        self.venv_dir = self.base_dir / "pico_venv"
        
        # Determine Python executable in venv
        if self.is_windows:
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
            self.venv_pip = self.venv_dir / "Scripts" / "pip.exe"
        else:
            self.venv_python = self.venv_dir / "bin" / "python"
            self.venv_pip = self.venv_dir / "bin" / "pip"
            
    def check_python(self):
        """Check if Python is properly installed"""
        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro} detected")
        if version.major < 3 or (version.major == 3 and version.minor < 6):
            print("ERROR: Python 3.6 or higher is required")
            return False
        return True
    
    def create_virtual_environment(self):
        """Create and setup virtual environment"""
        print("\nSetting up virtual environment...")
        
        if self.venv_dir.exists():
            print("Virtual environment already exists")
            return True
            
        try:
            # Create venv
            venv.create(self.venv_dir, with_pip=True)
            print("Created virtual environment")
            
            # Upgrade pip in venv
            subprocess.check_call([str(self.venv_python), "-m", "pip", 
                                 "install", "--upgrade", "pip"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print("Upgraded pip in virtual environment")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create virtual environment: {e}")
            return False
        
    def install_dependencies(self):
        """Install required Python packages in virtual environment"""
        print("\nInstalling dependencies...")
        
        # Create requirements.txt if it doesn't exist
        requirements = [
            "mpremote>=1.20.0",
            "pyserial>=3.5",
            "watchdog>=2.1.9",
            "requests>=2.28.0"
        ]
        
        if self.is_windows:
            requirements.append("pywin32>=300")
            
        requirements_file = self.base_dir / "requirements.txt"
        if not requirements_file.exists():
            with open(requirements_file, "w") as f:
                f.write("\n".join(requirements))
            print("Created requirements.txt")
            
        try:
            # Install from requirements
            print("Installing packages...")
            subprocess.check_call([str(self.venv_pip), "install", "-r", 
                                 str(requirements_file)],
                                stdout=subprocess.DEVNULL)
            
            # Verify critical packages
            critical_packages = {
                'mpremote': 'mpremote',
                'pyserial': 'serial',
                'watchdog': 'watchdog'
            }
            
            for package, import_name in critical_packages.items():
                try:
                    subprocess.check_call([str(self.venv_python), "-c", 
                                         f"import {import_name}"],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
                    print(f"✓ {package} installed successfully")
                except:
                    print(f"✗ {package} failed to install")
                    return False
                    
            print("\nAll dependencies installed successfully!")
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
cd /d "%~dp0"
if not exist "pico_venv\\Scripts\\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run pico_installer.py first
    pause
    exit /b 1
)
"pico_venv\\Scripts\\python.exe" "pico_sync_manager.py" %*
if errorlevel 1 pause
'''
        with open("PicoSync.bat", "w") as f:
            f.write(launcher_content)
        print("Created PicoSync.bat launcher")
        
    def create_linux_launcher(self):
        """Create Linux shell script launcher"""
        launcher_content = f'''#!/bin/bash
cd "$(dirname "$0")"

if [ ! -f "pico_venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run pico_installer.py first"
    exit 1
fi

./pico_venv/bin/python pico_sync_manager.py "$@"
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
            # Try using pywin32 if available
            import win32com.client
            desktop = Path.home() / "Desktop"
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(desktop / "PicoSync.lnk"))
            shortcut.Targetpath = str(Path.cwd() / "PicoSync.bat")
            shortcut.WorkingDirectory = str(Path.cwd())
            shortcut.IconLocation = str(self.venv_python)
            shortcut.save()
            print("Created desktop shortcut")
        except ImportError:
            print("Note: Desktop shortcut creation requires pywin32")
            
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
            try:
                groups = subprocess.getoutput("groups")
                if "dialout" not in groups:
                    print("WARNING: You may need to add your user to the 'dialout' group:")
                    print(f"  sudo usermod -a -G dialout {os.getlogin()}")
                    print("  Then log out and back in for changes to take effect")
            except:
                pass
                
    def download_firmware_files(self):
        """Pre-download MicroPython firmware files"""
        print("\nDownloading MicroPython firmware files...")
        
        firmware_dir = self.base_dir / "firmware"
        firmware_dir.mkdir(exist_ok=True)
        
        firmwares = {
            "RPI_PICO-latest.uf2": "https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2",
            "RPI_PICO2-latest.uf2": "https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
        }
        
        for filename, url in firmwares.items():
            filepath = firmware_dir / filename
            if filepath.exists():
                print(f"✓ {filename} already downloaded")
                continue
                
            try:
                # Use requests if available, otherwise urllib
                try:
                    import requests
                    response = requests.get(url, stream=True)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                except ImportError:
                    import urllib.request
                    urllib.request.urlretrieve(url, filepath)
                    
                print(f"✓ Downloaded {filename}")
                
            except Exception as e:
                print(f"✗ Failed to download {filename}: {e}")
                
    def run(self):
        """Run the installer"""
        print("=== PicoSync Universal Installer ===")
        print(f"Platform: {self.system}")
        
        if not self.check_python():
            return False
            
        if not self.create_virtual_environment():
            return False
            
        if not self.install_dependencies():
            return False
            
        self.create_launcher()
        self.create_desktop_shortcut()
        self.check_permissions()
        self.download_firmware_files()
        
        print("\n=== Installation Complete! ===")
        print("\nIMPORTANT: The application will run in a virtual environment")
        print("This ensures all dependencies are properly isolated\n")
        
        if self.is_windows:
            print("Run PicoSync.bat to start the application")
            print("Or double-click the desktop shortcut")
        else:
            print("Run ./PicoSync.sh to start the application")
            
        print("\nThe application will:")
        print("• Auto-detect when a Pico is connected")
        print("• Check if MicroPython is installed")
        print("• Offer to flash firmware if needed")
        print("• Sync your Python files automatically")
            
        return True

if __name__ == "__main__":
    installer = PicoInstaller()
    success = installer.run()
    
    if success and installer.is_windows:
        print("\nPress Enter to exit...")
        input()
        
    sys.exit(0 if success else 1)