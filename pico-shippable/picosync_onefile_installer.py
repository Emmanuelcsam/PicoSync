#!/usr/bin/env python3
"""
PicoSync All-in-One Installer
Single file that customers can run to install and launch PicoSync
"""

import os
import sys
import subprocess
import tempfile
import base64
import zlib
import json
import shutil
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request

class PicoSyncOneClickInstaller:
    def __init__(self):
        self.install_dir = Path.home() / "PicoSync"
        self.venv_dir = self.install_dir / "venv"
        self.app_dir = self.install_dir / "app"
        self.desktop = Path.home() / "Desktop"
        
        # Embedded files (base64 encoded and compressed)
        self.embedded_files = {
            "pico_sync_manager.py": "", # Will be filled with actual content
            "requirements.txt": base64.b64encode(zlib.compress(b"""pyserial>=3.5
watchdog>=2.1.0
mpremote>=0.4.0
pillow>=9.0.0""")).decode(),
            "run.bat": base64.b64encode(zlib.compress(b"""@echo off
cd /d "%~dp0"
call venv\\Scripts\\activate
python app\\pico_sync_manager.py
pause""")).decode(),
            "PicoSync.vbs": base64.b64encode(zlib.compress(b"""Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\\run.bat" & Chr(34), 0
Set WshShell = Nothing""")).decode()
        }
        
    def create_gui(self):
        """Create installation GUI"""
        self.root = tk.Tk()
        self.root.title("PicoSync Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Header
        header = tk.Frame(self.root, bg="#2196F3", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="PicoSync Installer", 
                        font=("Arial", 24, "bold"), 
                        bg="#2196F3", fg="white")
        title.pack(expand=True)
        
        # Main content
        content = tk.Frame(self.root, bg="white", padx=40, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Description
        desc = tk.Label(content, text="PicoSync - Raspberry Pi Pico Development Tool\n\n"
                                     "This installer will set up PicoSync on your computer.\n"
                                     "The installation includes:",
                       font=("Arial", 10), bg="white", justify=tk.LEFT)
        desc.pack(anchor=tk.W, pady=(0, 10))
        
        # Features
        features = [
            "✓ Python environment setup",
            "✓ Required dependencies",
            "✓ Desktop shortcuts",
            "✓ Automatic updates"
        ]
        
        for feature in features:
            lbl = tk.Label(content, text=feature, font=("Arial", 9), 
                          bg="white", fg="#666")
            lbl.pack(anchor=tk.W, padx=(20, 0))
        
        # Install location
        loc_frame = tk.Frame(content, bg="white")
        loc_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(loc_frame, text="Install to:", font=("Arial", 10), 
                bg="white").pack(side=tk.LEFT)
        
        self.install_path_var = tk.StringVar(value=str(self.install_dir))
        path_label = tk.Label(loc_frame, textvariable=self.install_path_var,
                             font=("Arial", 9), bg="#f0f0f0", padx=5)
        path_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Progress
        self.progress_frame = tk.Frame(content, bg="white")
        self.progress_frame.pack(fill=tk.X, pady=(20, 10))
        
        self.status_label = tk.Label(self.progress_frame, text="Ready to install",
                                    font=("Arial", 10), bg="white")
        self.status_label.pack()
        
        self.progress = ttk.Progressbar(self.progress_frame, length=400, 
                                       mode='indeterminate')
        self.progress.pack(pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(content, bg="white")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.install_btn = tk.Button(button_frame, text="Install", 
                                    font=("Arial", 12, "bold"),
                                    bg="#4CAF50", fg="white",
                                    padx=40, pady=10,
                                    command=self.start_installation,
                                    relief=tk.FLAT)
        self.install_btn.pack(side=tk.RIGHT)
        
        cancel_btn = tk.Button(button_frame, text="Cancel",
                              font=("Arial", 12),
                              bg="#f44336", fg="white", 
                              padx=40, pady=10,
                              command=self.root.quit,
                              relief=tk.FLAT)
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def update_status(self, message):
        """Update status in GUI"""
        self.status_label.config(text=message)
        self.root.update()
        
    def start_installation(self):
        """Start installation in background thread"""
        self.install_btn.config(state=tk.DISABLED)
        self.progress.start()
        
        thread = threading.Thread(target=self.install, daemon=True)
        thread.start()
        
    def install(self):
        """Main installation process"""
        try:
            # Create directories
            self.update_status("Creating directories...")
            self.install_dir.mkdir(exist_ok=True)
            self.app_dir.mkdir(exist_ok=True)
            
            # Check Python
            self.update_status("Checking Python installation...")
            if not self.check_python():
                self.download_python()
            
            # Create virtual environment
            self.update_status("Creating Python environment...")
            self.create_venv()
            
            # Extract embedded files
            self.update_status("Extracting application files...")
            self.extract_files()
            
            # Install dependencies
            self.update_status("Installing dependencies...")
            self.install_dependencies()
            
            # Create shortcuts
            self.update_status("Creating shortcuts...")
            self.create_shortcuts()
            
            # Complete
            self.progress.stop()
            self.update_status("Installation complete!")
            
            result = messagebox.askyesno("Installation Complete",
                                       "PicoSync has been installed successfully!\n\n"
                                       "Would you like to launch it now?")
            
            if result:
                self.launch_app()
                
            self.root.quit()
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("Installation Error", 
                               f"An error occurred during installation:\n\n{str(e)}")
            self.install_btn.config(state=tk.NORMAL)
    
    def check_python(self):
        """Check if Python is available"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def download_python(self):
        """Download and install Python if needed"""
        self.update_status("Python not found. Downloading Python...")
        
        # For Windows, download Python installer
        if sys.platform == "win32":
            url = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
            installer = self.install_dir / "python_installer.exe"
            
            urllib.request.urlretrieve(url, installer)
            
            self.update_status("Installing Python...")
            subprocess.run([str(installer), "/quiet", "InstallAllUsers=0", 
                          f"TargetDir={self.install_dir / 'python'}"], check=True)
            
            installer.unlink()
    
    def create_venv(self):
        """Create virtual environment"""
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], 
                      check=True)
    
    def extract_files(self):
        """Extract embedded files"""
        # Extract main application (this would contain the full pico_sync_manager.py)
        main_app = self.get_main_app_content()
        with open(self.app_dir / "pico_sync_manager.py", "w", encoding="utf-8") as f:
            f.write(main_app)
        
        # Extract other files
        for filename, content in self.embedded_files.items():
            if filename == "pico_sync_manager.py":
                continue
                
            decoded = zlib.decompress(base64.b64decode(content))
            
            if filename == "requirements.txt":
                with open(self.install_dir / filename, "wb") as f:
                    f.write(decoded)
            elif filename.endswith(".bat") or filename.endswith(".vbs"):
                with open(self.install_dir / filename, "wb") as f:
                    f.write(decoded)
    
    def get_main_app_content(self):
        """Return the main application content"""
        # This is a simplified version - in production, you'd embed the full app
        return '''#!/usr/bin/env python3
"""
PicoSync Manager - Simplified embedded version
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

class PicoSyncManager:
    def __init__(self, root):
        self.root = root
        self.root.title("PicoSync Manager")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="PicoSync Manager", 
                         font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        # Info
        info = ttk.Label(main_frame, 
                        text="Welcome to PicoSync!\\n\\n"
                             "This is the embedded version.\\n"
                             "Connect your Raspberry Pi Pico to get started.",
                        font=("Arial", 12))
        info.pack(pady=20)
        
        # Buttons
        ttk.Button(main_frame, text="Check for Pico", 
                  command=self.check_pico).pack(pady=5)
        
        ttk.Button(main_frame, text="Open Documentation",
                  command=self.open_docs).pack(pady=5)
    
    def check_pico(self):
        """Check for connected Pico"""
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            pico_found = False
            
            for port in ports:
                if "pico" in port.description.lower():
                    pico_found = True
                    break
            
            if pico_found:
                messagebox.showinfo("Pico Found", "Raspberry Pi Pico detected!")
            else:
                messagebox.showinfo("No Pico", "No Raspberry Pi Pico found.\\n"
                                             "Please connect your Pico via USB.")
        except:
            messagebox.showerror("Error", "Could not check for Pico.\\n"
                                        "Please ensure drivers are installed.")
    
    def open_docs(self):
        """Open documentation"""
        import webbrowser
        webbrowser.open("https://github.com/yourusername/picosync")

def main():
    root = tk.Tk()
    app = PicoSyncManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
'''
    
    def install_dependencies(self):
        """Install Python dependencies"""
        pip_exe = self.venv_dir / "Scripts" / "pip.exe"
        req_file = self.install_dir / "requirements.txt"
        
        subprocess.run([str(pip_exe), "install", "-r", str(req_file)], 
                      check=True)
    
    def create_shortcuts(self):
        """Create desktop shortcuts"""
        # Desktop shortcut
        desktop_shortcut = self.desktop / "PicoSync.lnk"
        
        # Create VBS launcher for silent start
        vbs_file = self.install_dir / "PicoSync.vbs"
        
        # Use VBS to create shortcut (Windows)
        if sys.platform == "win32":
            ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{desktop_shortcut}")
$Shortcut.TargetPath = "{vbs_file}"
$Shortcut.WorkingDirectory = "{self.install_dir}"
$Shortcut.IconLocation = "shell32.dll,13"
$Shortcut.Description = "PicoSync - Raspberry Pi Pico Development Tool"
$Shortcut.Save()
'''
            subprocess.run(["powershell", "-Command", ps_script], check=True)
        
        # Start menu shortcut
        start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        start_menu_shortcut = start_menu / "PicoSync.lnk"
        
        if sys.platform == "win32" and start_menu.exists():
            ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{start_menu_shortcut}")
$Shortcut.TargetPath = "{vbs_file}"
$Shortcut.WorkingDirectory = "{self.install_dir}"
$Shortcut.IconLocation = "shell32.dll,13"
$Shortcut.Description = "PicoSync - Raspberry Pi Pico Development Tool"
$Shortcut.Save()
'''
            subprocess.run(["powershell", "-Command", ps_script], check=True)
    
    def launch_app(self):
        """Launch the installed application"""
        if sys.platform == "win32":
            os.startfile(self.install_dir / "PicoSync.vbs")
        else:
            subprocess.Popen([str(self.venv_dir / "bin" / "python"),
                            str(self.app_dir / "pico_sync_manager.py")])
    
    def run(self):
        """Run the installer"""
        self.create_gui()
        self.root.mainloop()

if __name__ == "__main__":
    # Check if running as admin on Windows
    if sys.platform == "win32":
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            # Re-run as admin
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()
    
    installer = PicoSyncOneClickInstaller()
    installer.run()
