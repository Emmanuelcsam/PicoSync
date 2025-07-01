#!/usr/bin/env python3
"""
PicoSync Universal Installer with UV Support
Automatically sets up environment and installs dependencies
"""

import os
import sys
import subprocess
import platform
import shutil
import json
from pathlib import Path

class PicoSyncInstaller:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.config_dir = self.base_dir / "config"
        self.core_dir = self.config_dir / "core"
        self.venv_dir = self.base_dir / "pico_venv"
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        
        # UV executable paths
        self.uv_cmd = self.find_uv()
        
    def find_uv(self):
        """Find UV command in system"""
        # Check if uv is in PATH
        uv_cmd = shutil.which("uv")
        if uv_cmd:
            return uv_cmd
            
        # Check common locations
        home = Path.home()
        locations = [
            home / ".cargo" / "bin" / "uv",
            home / ".local" / "bin" / "uv",
            Path("/usr/local/bin/uv"),
            Path("/usr/bin/uv"),
        ]
        
        if self.is_windows:
            locations.extend([
                home / ".cargo" / "bin" / "uv.exe",
                home / "AppData" / "Local" / "Programs" / "uv" / "uv.exe",
            ])
            
        for loc in locations:
            if loc.exists():
                return str(loc)
                
        return None
        
    def install_uv(self):
        """Install UV if not found"""
        print("\n📦 UV not found. Installing UV package manager...")
        
        if self.is_windows:
            # Windows PowerShell installation
            ps_cmd = 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
            result = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print("Failed to install UV via PowerShell")
                print("Please install manually from: https://docs.astral.sh/uv/")
                return False
        else:
            # Unix installation
            curl_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
            result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print("Failed to install UV via curl")
                print("Please install manually from: https://docs.astral.sh/uv/")
                return False
                
        # Re-check for UV
        self.uv_cmd = self.find_uv()
        if not self.uv_cmd:
            # Try to add to PATH and check again
            if self.is_windows:
                os.environ["PATH"] = f"{Path.home()}/.cargo/bin;{os.environ['PATH']}"
            else:
                os.environ["PATH"] = f"{Path.home()}/.cargo/bin:{os.environ['PATH']}"
            self.uv_cmd = self.find_uv()
            
        return self.uv_cmd is not None
        
    def setup_virtual_environment(self):
        """Create virtual environment using UV"""
        print("\n🐍 Setting up Python virtual environment...")
        
        # Remove old venv if exists
        if self.venv_dir.exists():
            print("Removing old virtual environment...")
            shutil.rmtree(self.venv_dir)
            
        # Create new venv with UV
        cmd = [self.uv_cmd, "venv", str(self.venv_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to create virtual environment: {result.stderr}")
            return False
            
        print("✅ Virtual environment created successfully!")
        return True
        
    def install_dependencies(self):
        """Install dependencies using UV"""
        print("\n📥 Installing dependencies...")
        
        requirements_file = self.core_dir / "requirements.txt"
        if not requirements_file.exists():
            print("❌ requirements.txt not found!")
            return False
            
        # Install with UV
        cmd = [self.uv_cmd, "pip", "install", "-r", str(requirements_file)]
        
        # Set VIRTUAL_ENV for UV to use our venv
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(self.venv_dir)
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to install dependencies: {result.stderr}")
            return False
            
        # Install pywin32 on Windows for icon support
        if self.is_windows:
            print("\n📦 Installing pywin32 for icon support...")
            cmd_pywin32 = [self.uv_cmd, "pip", "install", "pywin32"]
            result_pywin32 = subprocess.run(cmd_pywin32, env=env, capture_output=True, text=True)
            
            if result_pywin32.returncode != 0:
                print("⚠️  Failed to install pywin32 (shortcuts will not have icons)")
            else:
                print("✅ pywin32 installed successfully!")
            
        print("✅ Dependencies installed successfully!")
        return True
        
    def create_config_file(self):
        """Create configuration file with paths"""
        config = {
            "base_dir": str(self.base_dir),
            "config_dir": str(self.config_dir),
            "core_dir": str(self.core_dir),
            "venv_dir": str(self.venv_dir),
            "system": self.system,
            "uv_cmd": self.uv_cmd
        }
        
        config_file = self.base_dir / "picosync_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
            
        print(f"✅ Configuration saved to {config_file}")
        
    def create_shortcuts(self):
        """Create desktop shortcuts"""
        print("\n🔗 Creating shortcuts...")
        
        if self.is_windows:
            # Create Start Menu shortcut
            start_menu = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
            shortcut_path = start_menu / "PicoSync.lnk"
            
            # Create .bat file for shortcut
            bat_path = self.base_dir / "PicoSync_Shortcut.bat"
            with open(bat_path, "w") as f:
                f.write(f'@echo off\ncd /d "{self.base_dir}"\ncall run_picosync.bat')
                
            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = str(bat_path)
                shortcut.WorkingDirectory = str(self.base_dir)
                shortcut.IconLocation = str(self.core_dir / "run.ico")
                shortcut.save()
                print(f"✅ Start Menu shortcut created")
            except:
                print("⚠️  Could not create Start Menu shortcut (install pywin32 for this feature)")
                
        elif self.is_linux:
            # Create desktop entry
            desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=PicoSync
Comment=Raspberry Pi Pico Sync Manager
Exec={self.base_dir}/run_picosync.sh
Icon={self.core_dir}/icon.ico
Terminal=false
Categories=Development;IDE;
"""
            
            desktop_dir = Path.home() / ".local/share/applications"
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            with open(desktop_dir / "picosync.desktop", "w") as f:
                f.write(desktop_entry)
                
            print("✅ Desktop entry created")
            
    def check_usb_permissions(self):
        """Check USB permissions on Linux"""
        if self.is_linux:
            groups = subprocess.getoutput("groups")
            if "dialout" not in groups:
                print("\n⚠️  USB Permission Warning:")
                print("You may need to add your user to the 'dialout' group:")
                print(f"  sudo usermod -a -G dialout {os.getlogin()}")
                print("Then log out and back in for changes to take effect.")
                
    def run(self):
        """Run the complete installation"""
        print("🚀 PicoSync Universal Installer")
        print("=" * 40)
        print(f"System: {self.system}")
        print(f"Base Directory: {self.base_dir}")
        
        # Check/Install UV
        if not self.uv_cmd:
            if not self.install_uv():
                print("\n❌ Failed to install UV. Please install manually.")
                return False
                
        print(f"\n✅ UV found at: {self.uv_cmd}")
        
        # Setup environment
        if not self.setup_virtual_environment():
            return False
            
        # Install dependencies
        if not self.install_dependencies():
            return False
            
        # Create config file
        self.create_config_file()
        
        # Create shortcuts
        self.create_shortcuts()
        
        # Check permissions
        self.check_usb_permissions()
        
        print("\n" + "=" * 40)
        print("✅ Installation Complete!")
        print("\nTo run PicoSync:")
        if self.is_windows:
            print("  - Double-click run_picosync.bat")
            print("  - Or use the Start Menu shortcut")
        else:
            print("  - Run: ./run_picosync.sh")
            print("  - Or use the application menu")
            
        return True

if __name__ == "__main__":
    installer = PicoSyncInstaller()
    success = installer.run()
    
    if not success:
        sys.exit(1)
        
    # Pause on Windows
    if installer.is_windows:
        input("\nPress Enter to exit...")