#!/usr/bin/env python3
"""
PicoSync Universal Runner
Runs PicoSync with proper environment setup
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class PicoSyncRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.config_file = self.base_dir / "picosync_config.json"
        
        # Load configuration
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            # Fallback if config doesn't exist
            self.config = {
                "base_dir": str(self.base_dir),
                "config_dir": str(self.base_dir / "config"),
                "core_dir": str(self.base_dir / "config" / "core"),
                "venv_dir": str(self.base_dir / "pico_venv"),
                "uv_cmd": "uv"
            }
            
        self.venv_dir = Path(self.config["venv_dir"])
        self.core_dir = Path(self.config["core_dir"])
        self.uv_cmd = self.config.get("uv_cmd", "uv")
        
    def check_installation(self):
        """Check if PicoSync is properly installed"""
        # Check virtual environment
        if not self.venv_dir.exists():
            print("❌ Virtual environment not found!")
            print("Please run the installer first:")
            print("  python install_picosync.py")
            return False
            
        # Check main script
        main_script = self.core_dir / "pico_sync_manager.py"
        if not main_script.exists():
            print("❌ PicoSync manager script not found!")
            print("Please ensure the config directory is properly set up.")
            return False
            
        return True
        
    def run_with_uv(self):
        """Run PicoSync using UV"""
        main_script = self.core_dir / "pico_sync_manager.py"
        
        # Set environment for UV
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(self.venv_dir)
        
        # Build command
        cmd = [self.uv_cmd, "run", "python", str(main_script)]
        
        print("🚀 Starting PicoSync...")
        print(f"Using virtual environment: {self.venv_dir}")
        
        try:
            # Run the application
            result = subprocess.run(cmd, env=env, cwd=str(self.base_dir))
            return result.returncode == 0
        except FileNotFoundError:
            print(f"\n❌ UV command not found: {self.uv_cmd}")
            print("Please ensure UV is installed and in your PATH")
            return False
        except KeyboardInterrupt:
            print("\n\n👋 PicoSync closed by user")
            return True
        except Exception as e:
            print(f"\n❌ Error running PicoSync: {e}")
            return False
            
    def run_direct(self):
        """Run PicoSync directly with Python from venv (fallback)"""
        main_script = self.core_dir / "pico_sync_manager.py"
        
        # Find Python in venv
        if sys.platform == "win32":
            python_exe = self.venv_dir / "Scripts" / "python.exe"
        else:
            python_exe = self.venv_dir / "bin" / "python"
            
        if not python_exe.exists():
            print("❌ Python not found in virtual environment!")
            return False
            
        print("🚀 Starting PicoSync (direct mode)...")
        
        try:
            # Run the application
            result = subprocess.run([str(python_exe), str(main_script)], cwd=str(self.base_dir))
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\n\n👋 PicoSync closed by user")
            return True
        except Exception as e:
            print(f"\n❌ Error running PicoSync: {e}")
            return False
            
    def run(self):
        """Run PicoSync"""
        print("=" * 40)
        print("PicoSync Runner")
        print("=" * 40)
        
        # Check installation
        if not self.check_installation():
            return False
            
        # Try running with UV first
        if self.run_with_uv():
            return True
            
        # Fallback to direct Python execution
        print("\n⚠️  UV run failed, trying direct execution...")
        return self.run_direct()

if __name__ == "__main__":
    runner = PicoSyncRunner()
    success = runner.run()
    
    if not success:
        # Pause on error
        if sys.platform == "win32":
            input("\nPress Enter to exit...")
        sys.exit(1)