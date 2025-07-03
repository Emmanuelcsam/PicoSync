#!/usr/bin/env python3
"""
PicoSync Standalone Edition
Single-file version that can be directly converted to executable
No external dependencies needed for basic operation

To create executable:
pyinstaller --onefile --windowed --name PicoSync picosync_standalone.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os
import sys
import json
import time
from pathlib import Path
import queue
from datetime import datetime

# Try to import optional dependencies
try:
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    
class MiniPicoSync:
    """Simplified PicoSync that works without external dependencies"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PicoSync - Standalone Edition")
        self.root.geometry("700x500")
        
        # Configuration
        self.config_file = Path.home() / ".picosync_standalone.json"
        self.config = self.load_config()
        
        # State
        self.sync_dir = self.config.get("sync_dir", "")
        self.pico_connected = False
        self.log_queue = queue.Queue()
        
        # Build UI
        self.setup_ui()
        
        # Start monitoring
        self.start_monitoring()
        
        # Process logs
        self.process_logs()
        
    def setup_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header, text="PicoSync", font=("Arial", 18, "bold")).pack(side=tk.LEFT)
        
        # Status indicator
        self.status_frame = ttk.Frame(header)
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_canvas = tk.Canvas(self.status_frame, width=16, height=16, highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 5))
        self.status_led = self.status_canvas.create_oval(2, 2, 14, 14, fill="red", outline="")
        
        self.status_label = ttk.Label(self.status_frame, text="Not Connected")
        self.status_label.pack(side=tk.LEFT)
        
        # Directory selection
        dir_frame = ttk.LabelFrame(main_frame, text="Sync Directory", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_label = ttk.Label(dir_frame, text=self.sync_dir or "No directory selected")
        self.dir_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="Browse", command=self.select_directory).pack(side=tk.RIGHT)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sync_btn = ttk.Button(button_frame, text="Sync Files", 
                                  command=self.sync_files, state=tk.DISABLED)
        self.sync_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.install_btn = ttk.Button(button_frame, text="Install Dependencies",
                                     command=self.install_dependencies)
        self.install_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Help", command=self.show_help).pack(side=tk.RIGHT)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log text with scrollbar
        scroll = ttk.Scrollbar(log_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(log_frame, height=10, yscrollcommand=scroll.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.log_text.yview)
        
        # Status bar
        self.statusbar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
    def load_config(self):
        """Load saved configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self):
        """Save configuration"""
        self.config["sync_dir"] = self.sync_dir
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def select_directory(self):
        """Select sync directory"""
        directory = filedialog.askdirectory(title="Select Directory to Sync")
        if directory:
            self.sync_dir = directory
            self.dir_label.config(text=directory)
            self.save_config()
            self.log(f"Sync directory set to: {directory}")
    
    def start_monitoring(self):
        """Start USB monitoring thread"""
        thread = threading.Thread(target=self.monitor_usb, daemon=True)
        thread.start()
    
    def monitor_usb(self):
        """Monitor for Pico connection"""
        while True:
            try:
                pico_found = False
                
                if SERIAL_AVAILABLE:
                    # Use serial library if available
                    ports = serial.tools.list_ports.comports()
                    for port in ports:
                        if "pico" in port.description.lower() or "2e8a" in port.hwid.lower():
                            pico_found = True
                            break
                else:
                    # Fallback: Try mpremote
                    try:
                        result = subprocess.run(["mpremote", "connect", "auto", "version"],
                                              capture_output=True, text=True, timeout=2)
                        pico_found = result.returncode == 0
                    except:
                        pass
                
                # Update connection status
                if pico_found != self.pico_connected:
                    self.pico_connected = pico_found
                    self.root.after(0, self.update_connection_status)
                    
            except Exception as e:
                self.log(f"Monitoring error: {e}", "ERROR")
                
            time.sleep(2)
    
    def update_connection_status(self):
        """Update UI based on connection status"""
        if self.pico_connected:
            self.status_canvas.itemconfig(self.status_led, fill="green")
            self.status_label.config(text="Connected")
            self.sync_btn.config(state=tk.NORMAL)
            self.log("Pico connected!")
        else:
            self.status_canvas.itemconfig(self.status_led, fill="red")
            self.status_label.config(text="Not Connected")
            self.sync_btn.config(state=tk.DISABLED)
            self.log("Pico disconnected")
    
    def sync_files(self):
        """Sync files to Pico"""
        if not self.sync_dir:
            messagebox.showwarning("No Directory", "Please select a directory to sync first")
            return
            
        if not self.pico_connected:
            messagebox.showwarning("Not Connected", "Please connect your Pico first")
            return
        
        # Run sync in thread
        thread = threading.Thread(target=self._do_sync, daemon=True)
        thread.start()
    
    def _do_sync(self):
        """Perform the actual sync"""
        self.log("Starting file sync...")
        self.root.after(0, lambda: self.statusbar.config(text="Syncing files..."))
        
        try:
            # Check if mpremote is available
            mpremote_cmd = self.find_mpremote()
            
            if not mpremote_cmd:
                self.log("mpremote not found. Please install dependencies.", "ERROR")
                self.root.after(0, lambda: messagebox.showerror(
                    "Missing Dependencies",
                    "mpremote is required for file sync.\n\n"
                    "Click 'Install Dependencies' to set it up."
                ))
                return
            
            # Get Python files
            py_files = list(Path(self.sync_dir).glob("*.py"))
            total = len(py_files)
            
            if total == 0:
                self.log("No Python files found in directory")
                return
            
            # Sync each file
            for i, file in enumerate(py_files):
                self.log(f"Syncing {file.name} ({i+1}/{total})")
                
                cmd = [mpremote_cmd, "connect", "auto", "cp", str(file), f":{file.name}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.log(f"Failed to sync {file.name}: {result.stderr}", "ERROR")
                else:
                    self.log(f"Synced {file.name}")
            
            self.log(f"Sync complete! {total} files transferred.")
            
        except Exception as e:
            self.log(f"Sync error: {e}", "ERROR")
        finally:
            self.root.after(0, lambda: self.statusbar.config(text="Ready"))
    
    def find_mpremote(self):
        """Find mpremote command"""
        # Check if in PATH
        if shutil.which("mpremote"):
            return "mpremote"
            
        # Check common locations
        if sys.platform == "win32":
            paths = [
                Path(sys.prefix) / "Scripts" / "mpremote.exe",
                Path.home() / ".local" / "bin" / "mpremote.exe",
            ]
        else:
            paths = [
                Path(sys.prefix) / "bin" / "mpremote",
                Path.home() / ".local" / "bin" / "mpremote",
            ]
        
        for path in paths:
            if path.exists():
                return str(path)
                
        return None
    
    def install_dependencies(self):
        """Install required dependencies"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Install Dependencies")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        ttk.Label(dialog, text="PicoSync Dependencies", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        info = tk.Text(dialog, height=8, width=50)
        info.pack(padx=10, pady=5)
        info.insert("1.0", "This will install:\n\n"
                          "• mpremote - For file transfer\n"
                          "• pyserial - For USB detection\n\n"
                          "Installation requires pip and internet connection.\n\n"
                          "Continue?")
        info.config(state=tk.DISABLED)
        
        def do_install():
            dialog.destroy()
            thread = threading.Thread(target=self._install_deps, daemon=True)
            thread.start()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Install", command=do_install).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)
    
    def _install_deps(self):
        """Install dependencies in background"""
        self.log("Installing dependencies...")
        
        try:
            # Install mpremote
            self.log("Installing mpremote...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "mpremote"],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("mpremote installed successfully")
            else:
                self.log(f"Failed to install mpremote: {result.stderr}", "ERROR")
                
            # Install pyserial
            self.log("Installing pyserial...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "pyserial"],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("pyserial installed successfully")
                global SERIAL_AVAILABLE
                SERIAL_AVAILABLE = True
            else:
                self.log(f"Failed to install pyserial: {result.stderr}", "ERROR")
                
            self.log("Installation complete!")
            
        except Exception as e:
            self.log(f"Installation error: {e}", "ERROR")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """PicoSync - Standalone Edition

Quick Start:
1. Connect your Raspberry Pi Pico via USB
2. Select a directory containing your Python files
3. Click 'Sync Files' to transfer them to the Pico

First Time Setup:
• Click 'Install Dependencies' to install required tools
• Make sure your Pico has MicroPython installed

Features:
• Automatic Pico detection
• One-click file synchronization
• Simple and lightweight

Troubleshooting:
• If Pico not detected, check USB cable
• If sync fails, install dependencies first
• For firmware flashing, use the full version

Version: 1.0 Standalone"""
        
        messagebox.showinfo("PicoSync Help", help_text)
    
    def log(self, message, level="INFO"):
        """Add log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_queue.put((log_entry, level))
    
    def process_logs(self):
        """Process log queue"""
        try:
            while True:
                log_entry, level = self.log_queue.get_nowait()
                
                # Insert with color based on level
                self.log_text.insert(tk.END, log_entry)
                
                if level == "ERROR":
                    # Color last line red
                    self.log_text.tag_add("error", "end-2c linestart", "end-1c")
                    self.log_text.tag_config("error", foreground="red")
                
                self.log_text.see(tk.END)
                
        except queue.Empty:
            pass
            
        self.root.after(100, self.process_logs)
    
    def on_closing(self):
        """Handle window close"""
        self.save_config()
        self.root.destroy()

def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set DPI awareness on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    app = MiniPicoSync(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    # Handle missing imports gracefully
    import shutil
    
    # Import what we can
    required_modules = []
    
    try:
        import serial.tools.list_ports
    except ImportError:
        required_modules.append("pyserial")
    
    # If running as script and modules missing, show dialog
    if required_modules and not getattr(sys, 'frozen', False):
        root = tk.Tk()
        root.withdraw()
        
        result = messagebox.askyesno(
            "Missing Dependencies",
            f"The following modules are not installed:\n"
            f"{', '.join(required_modules)}\n\n"
            "PicoSync will run with limited functionality.\n"
            "Install them now?"
        )
        
        if result:
            for module in required_modules:
                subprocess.run([sys.executable, "-m", "pip", "install", module])
            messagebox.showinfo("Installation Complete", 
                              "Dependencies installed. Please restart PicoSync.")
            sys.exit(0)
        
        root.destroy()
    
    main()
