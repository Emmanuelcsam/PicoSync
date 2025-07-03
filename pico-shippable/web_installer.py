#!/usr/bin/env python3
"""
PicoSync Web Installer
Tiny script that downloads and sets up everything automatically
Users only need to download this single small file
"""

import urllib.request
import os
import sys
import subprocess
import tempfile
import zipfile
import shutil
from pathlib import Path

PICOSYNC_VERSION = "1.0.0"
PYTHON_VERSION = "3.11.0"

# URLs for components
URLS = {
    "python_embed": f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip",
    "get_pip": "https://bootstrap.pypa.io/get-pip.py",
    # In production, host these files on GitHub releases or your server
    "app_files": "https://github.com/yourusername/picosync/releases/download/v{version}/app_files.zip"
}

def download_with_progress(url, filename):
    """Download file with progress bar"""
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '=' * filled + '-' * (bar_length - filled)
        sys.stdout.write(f'\r[{bar}] {percent:.1f}%')
        sys.stdout.flush()
    
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filename, report_progress)
    print()  # New line after progress bar

def main():
    print("=" * 60)
    print("PicoSync Web Installer")
    print("=" * 60)
    print()
    
    # Check if already installed
    install_dir = Path.home() / "PicoSync"
    if install_dir.exists():
        print(f"PicoSync is already installed at: {install_dir}")
        response = input("\nReinstall? (y/N): ").lower()
        if response != 'y':
            print("Installation cancelled.")
            return
        shutil.rmtree(install_dir)
    
    print(f"Installing to: {install_dir}")
    print()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            # Step 1: Download embedded Python
            python_zip = temp_path / "python-embed.zip"
            download_with_progress(URLS["python_embed"], python_zip)
            
            # Step 2: Extract Python
            print("Extracting Python...")
            install_dir.mkdir(parents=True)
            python_dir = install_dir / "python"
            
            with zipfile.ZipFile(python_zip, 'r') as zf:
                zf.extractall(python_dir)
            
            # Step 3: Configure Python
            print("Configuring Python...")
            pth_file = python_dir / "python311._pth"
            if pth_file.exists():
                content = pth_file.read_text()
                content = ".\n.\\Lib\n.\\Lib\\site-packages\n" + content
                content = content.replace("#import site", "import site")
                pth_file.write_text(content)
            
            # Step 4: Install pip
            print("Installing pip...")
            get_pip = temp_path / "get-pip.py"
            download_with_progress(URLS["get_pip"], get_pip)
            
            python_exe = python_dir / "python.exe"
            subprocess.run([str(python_exe), str(get_pip), "--no-warn-script-location"], 
                         check=True, capture_output=True)
            
            # Step 5: Install dependencies
            print("Installing dependencies...")
            subprocess.run([str(python_exe), "-m", "pip", "install", 
                          "mpremote", "pyserial", "watchdog", "--no-warn-script-location"],
                         check=True, capture_output=True)
            
            # Step 6: Create application
            print("Creating application files...")
            create_app_files(install_dir)
            
            # Step 7: Create shortcuts
            create_shortcuts(install_dir)
            
            print()
            print("=" * 60)
            print("Installation complete!")
            print()
            print(f"Installed to: {install_dir}")
            print()
            print("To run PicoSync:")
            print(f"  - Double-click: {install_dir}\\PicoSync.bat")
            print(f"  - Or find 'PicoSync' on your Desktop")
            print()
            
            # Offer to start
            response = input("Start PicoSync now? (Y/n): ").lower()
            if response != 'n':
                os.startfile(install_dir / "PicoSync.bat")
                
        except Exception as e:
            print(f"\nError during installation: {e}")
            print("Please try again or download the full package.")
            if install_dir.exists():
                shutil.rmtree(install_dir)
            sys.exit(1)

def create_app_files(install_dir):
    """Create the main application files"""
    
    # Main application (embedded as string for simplicity)
    app_py = '''
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
from pathlib import Path

class PicoSync:
    def __init__(self, root):
        self.root = root
        self.root.title("PicoSync")
        self.root.geometry("600x400")
        
        # UI
        frame = ttk.Frame(root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="PicoSync", font=("Arial", 16)).pack()
        
        # Directory
        self.dir_var = tk.StringVar(value="Select directory...")
        ttk.Label(frame, textvariable=self.dir_var).pack(pady=10)
        ttk.Button(frame, text="Browse", command=self.browse).pack()
        
        # Sync button
        ttk.Button(frame, text="Sync to Pico", command=self.sync).pack(pady=20)
        
        # Log
        self.log = tk.Text(frame, height=10)
        self.log.pack(fill=tk.BOTH, expand=True)
        
    def browse(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
            
    def sync(self):
        directory = self.dir_var.get()
        if directory == "Select directory...":
            messagebox.showwarning("No Directory", "Please select a directory first")
            return
            
        self.log.insert(tk.END, f"Syncing {directory}...\\n")
        
        # Find Python files and sync
        for file in Path(directory).glob("*.py"):
            try:
                cmd = ["mpremote", "connect", "auto", "cp", str(file), f":{file.name}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.log.insert(tk.END, f"✓ {file.name}\\n")
                else:
                    self.log.insert(tk.END, f"✗ {file.name}: {result.stderr}\\n")
            except Exception as e:
                self.log.insert(tk.END, f"Error: {e}\\n")
                
        self.log.insert(tk.END, "Sync complete!\\n")
        self.log.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PicoSync(root)
    root.mainloop()
'''
    
    # Write application
    app_dir = install_dir / "app"
    app_dir.mkdir(exist_ok=True)
    
    app_file = app_dir / "picosync.py"
    app_file.write_text(app_py)
    
    # Create batch launcher
    bat_content = f'''@echo off
cd /d "%~dp0"
python\\pythonw.exe app\\picosync.py
'''
    
    bat_file = install_dir / "PicoSync.bat"
    bat_file.write_text(bat_content)
    
    # Create VBS for silent launch
    vbs_content = '''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\\PicoSync.bat" & Chr(34), 0
Set WshShell = Nothing
'''
    
    vbs_file = install_dir / "PicoSync.vbs"
    vbs_file.write_text(vbs_content)

def create_shortcuts(install_dir):
    """Create desktop shortcut"""
    
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        return
        
    # PowerShell script to create shortcut
    ps_script = f'''
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{desktop}\\PicoSync.lnk")
$Shortcut.TargetPath = "{install_dir}\\PicoSync.vbs"
$Shortcut.WorkingDirectory = "{install_dir}"
$Shortcut.IconLocation = "imageres.dll,11"
$Shortcut.Description = "Raspberry Pi Pico Sync Manager"
$Shortcut.Save()
'''
    
    # Run PowerShell to create shortcut
    try:
        subprocess.run(["powershell", "-Command", ps_script], 
                      check=True, capture_output=True)
        print("Desktop shortcut created")
    except:
        print("Could not create desktop shortcut")

if __name__ == "__main__":
    # Make console stay open on Windows
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled.")
    
    if sys.platform == "win32":
        input("\nPress Enter to exit...")
