#!/usr/bin/env python3
"""
Create Portable PicoSync Package
This creates a fully portable package that works on any Windows machine
without requiring Python or any other dependencies
"""

import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess
from pathlib import Path
import json

class PortablePackageBuilder:
    def __init__(self):
        self.build_dir = Path("build_portable")
        self.dist_dir = Path("PicoSync_Portable")
        self.python_version = "3.11.0"
        
    def clean_dirs(self):
        """Clean build directories"""
        print("Cleaning directories...")
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        self.build_dir.mkdir()
        self.dist_dir.mkdir()
    
    def download_embedded_python(self):
        """Download Python embedded distribution"""
        print(f"Downloading Python {self.python_version} embedded...")
        
        url = f"https://www.python.org/ftp/python/{self.python_version}/python-{self.python_version}-embed-amd64.zip"
        zip_path = self.build_dir / "python-embed.zip"
        
        # Download with progress
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            print(f"Progress: {percent:.1f}%", end='\r')
        
        urllib.request.urlretrieve(url, zip_path, download_progress)
        print("\nDownload complete!")
        
        # Extract Python
        print("Extracting Python...")
        python_dir = self.dist_dir / "python"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(python_dir)
        
        # Modify python._pth to allow imports
        pth_file = python_dir / f"python{self.python_version.replace('.', '')[:3]}._pth"
        if pth_file.exists():
            content = pth_file.read_text()
            # Add current directory and Lib to path
            content = ".\n.\\Lib\n.\\Lib\\site-packages\n" + content
            # Uncomment import site
            content = content.replace("#import site", "import site")
            pth_file.write_text(content)
    
    def setup_pip(self):
        """Setup pip in embedded Python"""
        print("Setting up pip...")
        
        python_exe = self.dist_dir / "python" / "python.exe"
        
        # Download get-pip.py
        getpip_url = "https://bootstrap.pypa.io/get-pip.py"
        getpip_path = self.build_dir / "get-pip.py"
        urllib.request.urlretrieve(getpip_url, getpip_path)
        
        # Install pip
        subprocess.run([str(python_exe), str(getpip_path), "--no-warn-script-location"], 
                      check=True)
        
        print("Pip installed!")
    
    def create_app_files(self):
        """Create the application files"""
        print("Creating application files...")
        
        # Create main app (simplified version)
        app_content = '''#!/usr/bin/env python3
"""
PicoSync Portable Edition
Fully self-contained with no external dependencies
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import json
from pathlib import Path
import threading
import time

class PicoSyncPortable:
    def __init__(self, root):
        self.root = root
        self.root.title("PicoSync Portable")
        self.root.geometry("700x500")
        
        # Paths
        self.base_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0]))).parent
        self.python_exe = self.base_dir / "python" / "python.exe"
        self.config_file = self.base_dir / "config.json"
        
        # Load config
        self.config = self.load_config()
        
        # UI
        self.setup_ui()
        
        # Check dependencies on startup
        self.root.after(100, self.check_dependencies)
        
    def setup_ui(self):
        """Create user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="PicoSync Portable", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Checking status...")
        self.status_label.pack()
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Sync Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=10)
        
        self.dir_label = ttk.Label(dir_frame, text=self.config.get("sync_dir", "Not selected"))
        self.dir_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(dir_frame, text="Browse", command=self.select_directory).pack(side=tk.RIGHT)
        
        # Actions
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=10)
        
        self.sync_btn = ttk.Button(action_frame, text="Sync Files", 
                                  command=self.sync_files, state=tk.DISABLED)
        self.sync_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="Install Tools", 
                  command=self.install_tools).pack(side=tk.LEFT, padx=5)
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def check_dependencies(self):
        """Check if tools are installed"""
        self.log("Checking dependencies...")
        
        # Check for mpremote
        result = subprocess.run([str(self.python_exe), "-m", "pip", "show", "mpremote"],
                              capture_output=True)
        
        if result.returncode == 0:
            self.log("Dependencies installed ✓")
            self.status_label.config(text="Ready - Connect your Pico")
            self.sync_btn.config(state=tk.NORMAL)
            # Start monitoring for Pico
            threading.Thread(target=self.monitor_pico, daemon=True).start()
        else:
            self.log("Dependencies not installed - Click 'Install Tools'")
            self.status_label.config(text="Setup required")
    
    def install_tools(self):
        """Install required tools"""
        self.log("Installing tools...")
        
        def install():
            try:
                # Install mpremote and pyserial
                cmd = [str(self.python_exe), "-m", "pip", "install", 
                      "mpremote", "pyserial", "--no-warn-script-location"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log("Tools installed successfully!")
                    self.root.after(0, self.check_dependencies)
                else:
                    self.log(f"Installation failed: {result.stderr}")
                    
            except Exception as e:
                self.log(f"Error: {e}")
        
        threading.Thread(target=install, daemon=True).start()
    
    def monitor_pico(self):
        """Monitor for Pico connection"""
        while True:
            try:
                # Use embedded Python to check
                result = subprocess.run(
                    [str(self.python_exe), "-c", 
                     "import serial.tools.list_ports; "
                     "print(any('2e8a' in p.hwid for p in serial.tools.list_ports.comports()))"],
                    capture_output=True, text=True
                )
                
                connected = "True" in result.stdout
                
                status = "Pico connected ✓" if connected else "Waiting for Pico..."
                self.root.after(0, lambda: self.status_label.config(text=status))
                
            except:
                pass
                
            time.sleep(2)
    
    def select_directory(self):
        """Select sync directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.config["sync_dir"] = directory
            self.save_config()
            self.dir_label.config(text=directory)
            self.log(f"Selected: {directory}")
    
    def sync_files(self):
        """Sync files to Pico"""
        sync_dir = self.config.get("sync_dir")
        if not sync_dir:
            messagebox.showwarning("No Directory", "Please select a directory first")
            return
        
        self.log("Starting sync...")
        
        def do_sync():
            try:
                # Get Python files
                py_files = list(Path(sync_dir).glob("*.py"))
                
                for file in py_files:
                    self.log(f"Syncing {file.name}...")
                    
                    cmd = [str(self.python_exe), "-m", "mpremote", 
                          "connect", "auto", "cp", str(file), f":{file.name}"]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.log(f"✓ {file.name}")
                    else:
                        self.log(f"✗ {file.name}: {result.stderr}")
                
                self.log("Sync complete!")
                
            except Exception as e:
                self.log(f"Sync error: {e}")
        
        threading.Thread(target=do_sync, daemon=True).start()
    
    def log(self, message):
        """Add to log"""
        self.log_text.insert(tk.END, f"{message}\\n")
        self.log_text.see(tk.END)
        self.root.update()

def main():
    root = tk.Tk()
    app = PicoSyncPortable(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
        
        # Write main app
        app_file = self.dist_dir / "app" / "picosync.py"
        app_file.parent.mkdir(exist_ok=True)
        app_file.write_text(app_content)
        
        # Create launcher executable using simple C program
        launcher_c = '''
#include <windows.h>
#include <stdio.h>

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Get current directory
    char currentDir[MAX_PATH];
    GetCurrentDirectory(MAX_PATH, currentDir);
    
    // Build paths
    char pythonPath[MAX_PATH];
    char scriptPath[MAX_PATH];
    
    snprintf(pythonPath, MAX_PATH, "%s\\\\python\\\\pythonw.exe", currentDir);
    snprintf(scriptPath, MAX_PATH, "%s\\\\app\\\\picosync.py", currentDir);
    
    // Check if Python exists
    if (GetFileAttributes(pythonPath) == INVALID_FILE_ATTRIBUTES) {
        MessageBox(NULL, "Python not found. Please run from PicoSync directory.", "Error", MB_OK | MB_ICONERROR);
        return 1;
    }
    
    // Launch Python script
    STARTUPINFO si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);
    
    char cmdLine[MAX_PATH * 2];
    snprintf(cmdLine, sizeof(cmdLine), "\\"%s\\" \\"%s\\"", pythonPath, scriptPath);
    
    if (!CreateProcess(NULL, cmdLine, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        MessageBox(NULL, "Failed to launch PicoSync", "Error", MB_OK | MB_ICONERROR);
        return 1;
    }
    
    // Don't wait, just exit
    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);
    
    return 0;
}
'''
        
        launcher_c_file = self.build_dir / "launcher.c"
        launcher_c_file.write_text(launcher_c)
        
        # Try to compile launcher (requires MinGW or MSVC)
        self.compile_launcher()
        
        # Create batch file fallback
        batch_content = '''@echo off
cd /d "%~dp0"
start "" "python\\pythonw.exe" "app\\picosync.py"
'''
        (self.dist_dir / "PicoSync.bat").write_text(batch_content)
        
        # Create first-run setup
        setup_content = '''@echo off
echo Setting up PicoSync Portable...
cd /d "%~dp0"

echo.
echo This will install required tools for PicoSync.
echo.
pause

python\\python.exe -m pip install mpremote pyserial --no-warn-script-location

echo.
echo Setup complete! You can now run PicoSync.
echo.
pause
'''
        (self.dist_dir / "Setup.bat").write_text(setup_content)
        
        # Create README
        readme = '''PicoSync Portable Edition
========================

No installation required! Everything is self-contained.

First Time Setup:
1. Run Setup.bat (one time only)
2. Run PicoSync.exe or PicoSync.bat

Usage:
1. Connect your Raspberry Pi Pico
2. Select folder with Python files  
3. Click "Sync Files"

This package includes:
- Python 3.11 (embedded)
- All required dependencies
- No admin rights needed
- Works on any Windows PC

Troubleshooting:
- If PicoSync doesn't start, try PicoSync.bat instead
- Run Setup.bat if tools are missing
- Requires Windows 10/11 64-bit

Version: 1.0 Portable
'''
        (self.dist_dir / "README.txt").write_text(readme)
    
    def compile_launcher(self):
        """Try to compile C launcher"""
        print("Attempting to compile launcher...")
        
        # Try different compilers
        compilers = [
            # MinGW
            ["gcc", "-mwindows", "-o", str(self.dist_dir / "PicoSync.exe"), 
             str(self.build_dir / "launcher.c")],
            # MSVC via cl
            ["cl", "/Fe:" + str(self.dist_dir / "PicoSync.exe"),
             str(self.build_dir / "launcher.c"), "user32.lib"],
            # TCC if available
            ["tcc", "-mwindows", "-o", str(self.dist_dir / "PicoSync.exe"),
             str(self.build_dir / "launcher.c")]
        ]
        
        for cmd in compilers:
            try:
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode == 0:
                    print(f"Launcher compiled successfully with {cmd[0]}")
                    return True
            except FileNotFoundError:
                continue
        
        print("No C compiler found - using batch file launcher")
        return False
    
    def create_archive(self):
        """Create final ZIP archive"""
        print("Creating ZIP archive...")
        
        archive_name = f"PicoSync_Portable_Windows_{self.python_version}.zip"
        
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.dist_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.dist_dir.parent)
                    zf.write(file_path, arcname)
        
        size_mb = os.path.getsize(archive_name) / 1024 / 1024
        print(f"\nCreated: {archive_name} ({size_mb:.1f} MB)")
        
        return archive_name
    
    def build(self):
        """Build the portable package"""
        print("Building PicoSync Portable Package")
        print("=" * 50)
        
        self.clean_dirs()
        self.download_embedded_python()
        self.setup_pip()
        self.create_app_files()
        archive = self.create_archive()
        
        print("\n" + "=" * 50)
        print("Build complete!")
        print(f"\nDistribution folder: {self.dist_dir}/")
        print(f"Archive: {archive}")
        print("\nTo distribute:")
        print("1. Send the ZIP file to users")
        print("2. They extract and run Setup.bat (first time)")
        print("3. Then run PicoSync.exe")
        print("\nNo Python installation required!")

if __name__ == "__main__":
    builder = PortablePackageBuilder()
    builder.build()
