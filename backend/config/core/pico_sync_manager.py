#!/usr/bin/env python3
"""
Pico Sync Manager - Automated Raspberry Pi Pico Development Tool
A comprehensive GUI application for managing Pico firmware and file synchronization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import queue
import time
import os
import sys
import json
import hashlib
import shutil
from pathlib import Path
import platform
import webbrowser
from datetime import datetime
import serial.tools.list_ports
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration file path
CONFIG_FILE = Path.home() / ".pico_sync_config.json"
LOG_FILE = Path.home() / ".pico_sync_log.txt"

class PicoFileWatcher(FileSystemEventHandler):
    """Watches for file changes in the configured directory"""
    def __init__(self, callback):
        self.callback = callback
        self.last_modified = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            # Debounce - only trigger if file hasn't been modified in last second
            current_time = time.time()
            if event.src_path in self.last_modified:
                if current_time - self.last_modified[event.src_path] < 1:
                    return
            self.last_modified[event.src_path] = current_time
            self.callback(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            time.sleep(0.1)  # Wait for file to be fully written
            self.callback(event.src_path)

class PicoSyncManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Pico Sync Manager")
        self.root.geometry("800x600")
        
        # Set icon and theme
        self.root.configure(bg='#1e1e1e')
        
        # State variables
        self.config = self.load_config()
        self.pico_connected = False
        self.auto_sync_enabled = tk.BooleanVar(value=self.config.get('auto_sync', True))
        self.sync_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.current_port = None
        self.file_observer = None
        self.pico_model = None  # Will detect RP2040 or RP2350
        self.is_windows = platform.system() == 'Windows'
        
        # Create UI
        self.create_ui()
        
        # Start background threads
        self.start_monitoring()
        
        # Check dependencies on startup
        self.root.after(100, self.check_dependencies)
        
        # Start log processor
        self.process_logs()
        
    def create_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header with status
        self.create_header(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Main content area with tabs
        self.create_content_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create header with connection status"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Title
        title = ttk.Label(header_frame, text="Pico Sync Manager", 
                         font=('Helvetica', 16, 'bold'))
        title.grid(row=0, column=0, sticky=tk.W)
        
        # Connection status with LED indicator
        status_frame = ttk.Frame(header_frame)
        status_frame.grid(row=0, column=1, sticky=tk.E)
        
        # LED Canvas
        self.led_canvas = tk.Canvas(status_frame, width=20, height=20, 
                                   highlightthickness=0, bg='#1e1e1e')
        self.led_canvas.grid(row=0, column=0, padx=(0, 5))
        
        # Draw LED
        self.led = self.led_canvas.create_oval(2, 2, 18, 18, 
                                               fill='#ff0000', outline='')
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Disconnected", 
                                     font=('Helvetica', 10))
        self.status_label.grid(row=0, column=1)
        
        # Pico model label
        self.model_label = ttk.Label(status_frame, text="", 
                                    font=('Helvetica', 9))
        self.model_label.grid(row=1, column=1, sticky=tk.E)
        
        # Configure column weight
        header_frame.columnconfigure(0, weight=1)
        
    def create_control_panel(self, parent):
        """Create control panel with settings"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Directory selection
        dir_frame = ttk.Frame(control_frame)
        dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(dir_frame, text="Sync Directory:").grid(row=0, column=0, sticky=tk.W)
        
        self.dir_var = tk.StringVar(value=self.config.get('sync_directory', ''))
        self.dir_label = ttk.Label(dir_frame, textvariable=self.dir_var, 
                                  relief=tk.SUNKEN, width=50)
        self.dir_label.grid(row=0, column=1, padx=10)
        
        ttk.Button(dir_frame, text="Browse", 
                  command=self.select_directory).grid(row=0, column=2)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Auto sync checkbox
        self.auto_sync_check = ttk.Checkbutton(button_frame, text="Auto Sync", 
                                               variable=self.auto_sync_enabled,
                                               command=self.toggle_auto_sync)
        self.auto_sync_check.grid(row=0, column=0, padx=5)
        
        # Manual sync button
        self.sync_button = ttk.Button(button_frame, text="Sync Now", 
                                     command=self.manual_sync,
                                     state=tk.DISABLED)
        self.sync_button.grid(row=0, column=1, padx=5)
        
        # Flash firmware button
        self.flash_button = ttk.Button(button_frame, text="Flash Firmware", 
                                      command=self.flash_firmware,
                                      state=tk.DISABLED)
        self.flash_button.grid(row=0, column=2, padx=5)
        
        # Wipe Pico button
        self.wipe_button = ttk.Button(button_frame, text="Wipe Pico", 
                                     command=self.wipe_pico,
                                     state=tk.DISABLED)
        self.wipe_button.grid(row=0, column=3, padx=5)
        
        # Reset button
        self.reset_button = ttk.Button(button_frame, text="Reset Pico", 
                                      command=self.reset_pico,
                                      state=tk.DISABLED)
        self.reset_button.grid(row=0, column=4, padx=5)
        
        # Configure grid weight
        control_frame.columnconfigure(0, weight=1)
        dir_frame.columnconfigure(1, weight=1)
        
    def create_content_area(self, parent):
        """Create tabbed content area"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sync tab
        self.create_sync_tab()
        
        # Files tab
        self.create_files_tab()
        
        # Log tab
        self.create_log_tab()
        
        # Settings tab
        self.create_settings_tab()
        
    def create_sync_tab(self):
        """Create sync status tab"""
        sync_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(sync_frame, text="Sync Status")
        
        # Progress frame
        progress_frame = ttk.LabelFrame(sync_frame, text="Current Operation", 
                                       padding="10")
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.operation_label = ttk.Label(progress_frame, text="Idle")
        self.operation_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # File queue
        queue_frame = ttk.LabelFrame(sync_frame, text="Sync Queue", padding="10")
        queue_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Queue listbox with scrollbar
        queue_scroll = ttk.Scrollbar(queue_frame)
        queue_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.queue_listbox = tk.Listbox(queue_frame, 
                                       yscrollcommand=queue_scroll.set,
                                       height=10)
        self.queue_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        queue_scroll.config(command=self.queue_listbox.yview)
        
        # Configure grid weights
        sync_frame.columnconfigure(0, weight=1)
        sync_frame.rowconfigure(1, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        
    def create_files_tab(self):
        """Create file management tab"""
        files_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(files_frame, text="File Manager")
        
        # Split into local and Pico files
        paned = ttk.PanedWindow(files_frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Local files
        local_frame = ttk.LabelFrame(paned, text="Local Files", padding="10")
        paned.add(local_frame, weight=1)
        
        local_scroll = ttk.Scrollbar(local_frame)
        local_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.local_tree = ttk.Treeview(local_frame, 
                                      yscrollcommand=local_scroll.set,
                                      columns=('size', 'modified'),
                                      height=15)
        self.local_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        local_scroll.config(command=self.local_tree.yview)
        
        self.local_tree.heading('#0', text='Name')
        self.local_tree.heading('size', text='Size')
        self.local_tree.heading('modified', text='Modified')
        
        # Pico files
        pico_frame = ttk.LabelFrame(paned, text="Pico Files", padding="10")
        paned.add(pico_frame, weight=1)
        
        pico_scroll = ttk.Scrollbar(pico_frame)
        pico_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.pico_tree = ttk.Treeview(pico_frame, 
                                     yscrollcommand=pico_scroll.set,
                                     columns=('size',),
                                     height=15)
        self.pico_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        pico_scroll.config(command=self.pico_tree.yview)
        
        self.pico_tree.heading('#0', text='Name')
        self.pico_tree.heading('size', text='Size')
        
        # File operations buttons
        ops_frame = ttk.Frame(pico_frame)
        ops_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        ttk.Button(ops_frame, text="Upload Selected", 
                  command=self.upload_selected).grid(row=0, column=0, padx=2)
        ttk.Button(ops_frame, text="Delete Selected", 
                  command=self.delete_selected).grid(row=0, column=1, padx=2)
        ttk.Button(ops_frame, text="Refresh", 
                  command=self.refresh_files).grid(row=0, column=2, padx=2)
        
        # Configure grid weights
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        local_frame.columnconfigure(0, weight=1)
        local_frame.rowconfigure(0, weight=1)
        pico_frame.columnconfigure(0, weight=1)
        pico_frame.rowconfigure(0, weight=1)
        
    def create_log_tab(self):
        """Create log viewer tab"""
        log_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(log_frame, text="Logs")
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log control buttons
        control_frame = ttk.Frame(log_frame)
        control_frame.grid(row=1, column=0, pady=5)
        
        ttk.Button(control_frame, text="Clear Log", 
                  command=self.clear_log).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Save Log", 
                  command=self.save_log).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings options
        row = 0
        
        # File types to sync
        ttk.Label(settings_frame, text="File Types to Sync:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        
        self.file_types_var = tk.StringVar(
            value=self.config.get('file_types', '*.py'))
        file_types_entry = ttk.Entry(settings_frame, textvariable=self.file_types_var, 
                                    width=30)
        file_types_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Sync subdirectories
        self.sync_subdirs_var = tk.BooleanVar(
            value=self.config.get('sync_subdirs', True))
        ttk.Checkbutton(settings_frame, text="Sync Subdirectories", 
                       variable=self.sync_subdirs_var).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        # Auto flash on first connect
        self.auto_flash_var = tk.BooleanVar(
            value=self.config.get('auto_flash', False))
        ttk.Checkbutton(settings_frame, text="Auto Flash Firmware on First Connect", 
                       variable=self.auto_flash_var).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        # Show notifications
        self.show_notifications_var = tk.BooleanVar(
            value=self.config.get('show_notifications', True))
        ttk.Checkbutton(settings_frame, text="Show Desktop Notifications", 
                       variable=self.show_notifications_var).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        # Log level
        ttk.Label(settings_frame, text="Log Level:").grid(
            row=row, column=0, sticky=tk.W, pady=5)
        
        self.log_level_var = tk.StringVar(
            value=self.config.get('log_level', 'INFO'))
        log_level_combo = ttk.Combobox(settings_frame, 
                                      textvariable=self.log_level_var,
                                      values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                                      state='readonly', width=15)
        log_level_combo.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # Save button
        ttk.Button(settings_frame, text="Save Settings", 
                  command=self.save_settings).grid(
            row=row, column=0, pady=20)
        
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_text = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_text)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(status_frame, text="v1.0.0", 
                                 font=('Helvetica', 8))
        version_label.grid(row=0, column=1, sticky=tk.E)
        
        status_frame.columnconfigure(0, weight=1)
        
    def load_config(self):
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self):
        """Save configuration to file"""
        self.config['sync_directory'] = self.dir_var.get()
        self.config['auto_sync'] = self.auto_sync_enabled.get()
        self.config['file_types'] = self.file_types_var.get()
        self.config['sync_subdirs'] = self.sync_subdirs_var.get()
        self.config['auto_flash'] = self.auto_flash_var.get()
        self.config['show_notifications'] = self.show_notifications_var.get()
        self.config['log_level'] = self.log_level_var.get()
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_dependencies(self):
        """Check and install required dependencies"""
        self.log("Checking dependencies...", "INFO")
        
        required_packages = {
            'mpremote': 'mpremote',
            'pyserial': 'serial',
            'watchdog': 'watchdog'
        }
        
        missing = []
        for package, import_name in required_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                missing.append(package)
        
        if missing:
            self.log(f"Missing packages: {', '.join(missing)}", "WARNING")
            if messagebox.askyesno("Install Dependencies", 
                                  f"Missing packages: {', '.join(missing)}\n\n"
                                  "Would you like to install them now?"):
                self.install_dependencies(missing)
        else:
            self.log("All dependencies satisfied", "INFO")
    
    def install_dependencies(self, packages):
        """Install missing dependencies"""
        self.operation_label.config(text="Installing dependencies...")
        self.progress_bar.start()
        
        def install():
            for package in packages:
                self.log(f"Installing {package}...", "INFO")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", 
                                         "install", package])
                    self.log(f"Installed {package}", "SUCCESS")
                except subprocess.CalledProcessError as e:
                    self.log(f"Failed to install {package}: {e}", "ERROR")
            
            self.root.after(0, self.installation_complete)
        
        threading.Thread(target=install, daemon=True).start()
    
    def installation_complete(self):
        """Called when dependency installation is complete"""
        self.progress_bar.stop()
        self.operation_label.config(text="Idle")
        self.log("Dependency installation complete", "INFO")
        messagebox.showinfo("Installation Complete", 
                          "Dependencies installed. Please restart the application.")
    
    def start_monitoring(self):
        """Start background monitoring threads"""
        # USB monitoring thread
        usb_thread = threading.Thread(target=self.monitor_usb, daemon=True)
        usb_thread.start()
        
        # Sync processing thread
        sync_thread = threading.Thread(target=self.process_sync_queue, daemon=True)
        sync_thread.start()
    
    def monitor_usb(self):
        """Monitor for Pico USB connection"""
        bootsel_detected = False
        while True:
            try:
                # Check for BOOTSEL mode (appears as a drive)
                bootsel_drive = self.find_bootsel_drive()
                
                if bootsel_drive and not bootsel_detected:
                    bootsel_detected = True
                    self.root.after(0, lambda: self.on_bootsel_detected(bootsel_drive))
                elif not bootsel_drive and bootsel_detected:
                    bootsel_detected = False
                    
                # Check for normal Pico connection
                ports = serial.tools.list_ports.comports()
                pico_port = None
                
                for port in ports:
                    # Check for Pico identifiers
                    if (('2e8a' in port.hwid.lower() or 
                         'raspberry pi pico' in port.description.lower() or
                         'pico' in port.description.lower())):
                        pico_port = port.device
                        break
                
                if pico_port and not self.pico_connected:
                    # Pico connected
                    self.current_port = pico_port
                    self.pico_connected = True
                    self.root.after(0, self.on_pico_connected)
                elif not pico_port and self.pico_connected:
                    # Pico disconnected
                    self.pico_connected = False
                    self.current_port = None
                    self.root.after(0, self.on_pico_disconnected)
                
            except Exception as e:
                self.log(f"USB monitoring error: {e}", "ERROR")
            
            time.sleep(1)
    
    def find_bootsel_drive(self):
        """Find Pico in BOOTSEL mode"""
        # Windows drives
        if self.is_windows:
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    info_file = os.path.join(drive, "INFO_UF2.TXT")
                    if os.path.exists(info_file):
                        return drive
        else:
            # Linux/Mac mount points
            for mount in ['/media', '/mnt', '/Volumes']:
                if os.path.exists(mount):
                    for folder in os.listdir(mount):
                        path = os.path.join(mount, folder)
                        info_file = os.path.join(path, "INFO_UF2.TXT")
                        if os.path.exists(info_file):
                            return path
        return None
    
    def on_bootsel_detected(self, drive):
        """Handle BOOTSEL mode detection"""
        self.log(f"Pico detected in BOOTSEL mode at {drive}", "INFO")
        self.update_status("BOOTSEL Mode", "#ffaa00")
        
        # Detect model from INFO_UF2.TXT
        model = self.detect_model_from_bootsel(drive)
        if model:
            self.model_label.config(text=f"BOOTSEL: {model}")
            
        # Offer to flash if auto-flash is enabled
        if self.config.get('auto_flash', False):
            if messagebox.askyesno("Flash Firmware?", 
                                  f"Pico detected in BOOTSEL mode.\n"
                                  f"Model: {model or 'Unknown'}\n\n"
                                  "Flash MicroPython firmware now?"):
                self.flash_firmware_bootsel(drive, model)
                
    def detect_model_from_bootsel(self, drive):
        """Detect Pico model from BOOTSEL drive"""
        try:
            info_file = os.path.join(drive, "INFO_UF2.TXT")
            with open(info_file, 'r') as f:
                content = f.read()
                if "RP2350" in content:
                    return "Pico 2 (RP2350)"
                elif "RP2040" in content:
                    return "Pico (RP2040)"
        except:
            pass
        return None
    
    def flash_firmware_bootsel(self, drive, model):
        """Flash firmware when Pico is already in BOOTSEL mode"""
        self.operation_label.config(text="Downloading firmware...")
        self.progress_bar.start()
        
        def do_flash():
            try:
                # Determine firmware URL based on model
                if model and "RP2350" in model:
                    url = "https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
                    filename = "RPI_PICO2-latest.uf2"
                else:
                    url = "https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2"
                    filename = "RPI_PICO-latest.uf2"
                
                self.log(f"Downloading {filename}...", "INFO")
                
                import urllib.request
                urllib.request.urlretrieve(url, filename)
                self.log(f"Downloaded {filename}", "SUCCESS")
                
                # Copy firmware to BOOTSEL drive
                self.root.after(0, lambda: self.operation_label.config(text="Flashing firmware..."))
                shutil.copy2(filename, drive)
                self.log("Firmware flashed successfully!", "SUCCESS")
                
                # Clean up
                os.remove(filename)
                
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                                          "Firmware flashed! Pico will reboot automatically."))
                
            except Exception as e:
                self.log(f"Flash error: {e}", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to flash firmware: {e}"))
            finally:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self.operation_label.config(text="Idle"))
        
        threading.Thread(target=do_flash, daemon=True).start()
    
    def on_pico_connected(self):
        """Handle Pico connection"""
        self.log("Pico connected!", "SUCCESS")
        self.update_status("Connected", "#00ff00")
        
        # Enable buttons
        self.sync_button.config(state=tk.NORMAL)
        self.flash_button.config(state=tk.NORMAL)
        self.wipe_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        
        # Detect Pico model
        self.detect_pico_model()
        
        # Check if Pico needs firmware after a delay
        def check_and_flash():
            if self.config.get('auto_flash', False):
                if not self.check_micropython():
                    self.log("MicroPython not detected, prompting for flash", "WARNING")
                    if messagebox.askyesno("Flash Firmware?", 
                                          "MicroPython not detected.\n\n"
                                          "Flash firmware now?"):
                        self.flash_firmware()
                else:
                    self.log("MicroPython detected", "INFO")
        
        self.root.after(1000, check_and_flash)
        
        # Start file watching if auto sync enabled
        if self.auto_sync_enabled.get() and self.dir_var.get():
            self.start_file_watching()
            # Initial sync
            self.sync_all_files()
        
        # Refresh file lists
        self.refresh_files()
    
    def on_pico_disconnected(self):
        """Handle Pico disconnection"""
        self.log("Pico disconnected", "WARNING")
        self.update_status("Disconnected", "#ff0000")
        self.model_label.config(text="")
        
        # Disable buttons
        self.sync_button.config(state=tk.DISABLED)
        self.flash_button.config(state=tk.DISABLED) 
        self.wipe_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        
        # Stop file watching
        self.stop_file_watching()
        
        # Clear Pico file list
        self.pico_tree.delete(*self.pico_tree.get_children())
    
    def detect_pico_model(self):
        """Detect if it's RP2040 or RP2350"""
        try:
            # Try to get info from the Pico
            result = subprocess.run(['mpremote', 'connect', 'auto', 'exec', 
                                   'import sys; print(sys.implementation.name)'],
                                  capture_output=True, text=True, timeout=5)
            
            if 'rp2040' in result.stdout.lower():
                self.pico_model = "RP2040"
                self.model_label.config(text="Pico (RP2040)")
            elif 'rp2350' in result.stdout.lower():
                self.pico_model = "RP2350" 
                self.model_label.config(text="Pico 2 (RP2350)")
            else:
                self.model_label.config(text="Unknown Model")
        except:
            self.model_label.config(text="Model Detection Failed")
    
    def check_micropython(self):
        """Check if MicroPython is installed on Pico"""
        try:
            mpremote_cmd = 'mpremote' if shutil.which('mpremote') else str(Path.cwd() / 'Scripts' / 'mpremote.exe')
            result = subprocess.run([mpremote_cmd, 'connect', self.current_port or 'auto', 'ls'],
                                  capture_output=True, text=True, timeout=5)
            if result.stderr:
                self.log(f"MicroPython check stderr: {result.stderr}", "DEBUG")
            return result.returncode == 0
        except:
            return False
    
    def update_status(self, text, color):
        """Update connection status display"""
        self.status_label.config(text=text)
        self.led_canvas.itemconfig(self.led, fill=color)
    
    def select_directory(self):
        """Select sync directory"""
        directory = filedialog.askdirectory(
            title="Select Directory to Sync",
            initialdir=self.dir_var.get() or os.path.expanduser("~"))
        
        if directory:
            self.dir_var.set(directory)
            self.save_config()
            self.log(f"Sync directory set to: {directory}", "INFO")
            
            # Restart file watching if needed
            if self.pico_connected and self.auto_sync_enabled.get():
                self.stop_file_watching()
                self.start_file_watching()
                self.sync_all_files()
            
            # Refresh local files
            self.refresh_local_files()
    
    def toggle_auto_sync(self):
        """Toggle auto sync on/off"""
        if self.auto_sync_enabled.get():
            self.log("Auto sync enabled", "INFO")
            if self.pico_connected and self.dir_var.get():
                self.start_file_watching()
                self.sync_all_files()
        else:
            self.log("Auto sync disabled", "INFO")
            self.stop_file_watching()
        
        self.save_config()
    
    def start_file_watching(self):
        """Start watching directory for changes"""
        if not self.dir_var.get():
            return
        
        if not os.path.exists(self.dir_var.get()):
            return
        self.stop_file_watching()
        
        self.file_observer = Observer()
        handler = PicoFileWatcher(self.on_file_changed)
        self.file_observer.schedule(handler, self.dir_var.get(), 
                                   recursive=self.config.get('sync_subdirs', True))
        self.file_observer.start()
        self.log(f"Started watching: {self.dir_var.get()}", "INFO")
    
    def stop_file_watching(self):
        """Stop watching directory"""
        if self.file_observer and self.file_observer.is_alive():
            self.file_observer.stop()
            self.file_observer.join()
            self.file_observer = None
            self.log("Stopped file watching", "INFO")
    
    def on_file_changed(self, filepath):
        """Handle file change event"""
        self.log(f"File changed: {os.path.basename(filepath)}", "INFO")
        self.sync_queue.put(('file', filepath))
    
    def manual_sync(self):
        """Manually sync all files"""
        if not self.dir_var.get():
            messagebox.showwarning("No Directory", 
                                 "Please select a directory to sync first")
            return
        
        self.sync_all_files()
    
    def sync_all_files(self):
        """Sync all files in directory"""
        if not self.dir_var.get():
            return
        
        self.log("Starting full sync...", "INFO")
        self.sync_queue.put(('full', self.dir_var.get()))
    
    def process_sync_queue(self):
        """Process file sync queue in background"""
        while True:
            try:
                sync_type, data = self.sync_queue.get(timeout=1)
                
                if sync_type == 'file':
                    self.sync_single_file(data)
                elif sync_type == 'full':
                    self.sync_directory(data)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.log(f"Sync error: {e}", "ERROR")
    
    def sync_single_file(self, filepath):
        """Sync a single file to Pico"""
        if not self.pico_connected:
            return
        
        filename = os.path.basename(filepath)
        self.root.after(0, lambda: self.operation_label.config(
            text=f"Syncing {filename}..."))
        self.root.after(0, self.progress_bar.start)
        
        try:
            subprocess.run(['mpremote', 'connect', 'auto', 'cp', 
                          filepath, f':{filename}'],
                         check=True, capture_output=True, text=True)
            self.log(f"Synced: {filename}", "SUCCESS")
            self.root.after(0, self.refresh_files)
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to sync {filename}: {e}", "ERROR")
        finally:
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.operation_label.config(text="Idle"))
    
    def sync_directory(self, directory):
        """Sync entire directory to Pico"""
        if not self.pico_connected:
            return
        
        self.root.after(0, lambda: self.operation_label.config(
            text="Syncing directory..."))
        self.root.after(0, self.progress_bar.start)
        
        try:
            # Get list of Python files
            pattern = self.config.get('file_types', '*.py')
            files = []
            
            if self.config.get('sync_subdirs', True):
                for root, dirs, filenames in os.walk(directory):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            files.append(os.path.join(root, filename))
            else:
                files = [f for f in Path(directory).glob(pattern) if f.is_file()]
            
            # Clear queue display and add files
            self.root.after(0, lambda: self.queue_listbox.delete(0, tk.END))
            for f in files:
                self.root.after(0, lambda f=f: self.queue_listbox.insert(
                    tk.END, os.path.basename(f)))
            
            # Sync each file
            total = len(files)
            for i, filepath in enumerate(files):
                if not self.pico_connected:
                    break
                
                filename = os.path.basename(filepath)
                self.root.after(0, lambda f=filename, i=i, t=total: 
                              self.operation_label.config(
                                  text=f"Syncing {f} ({i+1}/{t})..."))
                
                try:
                    subprocess.run(['mpremote', 'connect', 'auto', 'cp', 
                                  str(filepath), f':{filename}'],
                                 check=True, capture_output=True, text=True)
                    self.log(f"Synced: {filename}", "SUCCESS")
                    
                    # Remove from queue display
                    self.root.after(0, lambda: self.queue_listbox.delete(0))
                    
                except subprocess.CalledProcessError as e:
                    self.log(f"Failed to sync {filename}: {e}", "ERROR")
            
            self.log(f"Directory sync complete: {total} files", "INFO")
            self.root.after(0, self.refresh_files)
            
        except Exception as e:
            self.log(f"Directory sync error: {e}", "ERROR")
        finally:
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.operation_label.config(text="Idle"))
            self.root.after(0, lambda: self.queue_listbox.delete(0, tk.END))
    
    def flash_firmware(self):
        """Flash MicroPython firmware to Pico"""
        # Create firmware selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Flash Firmware")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select Pico Model:", 
                 font=('Helvetica', 12)).pack(pady=10)
        
        model_var = tk.StringVar(value="auto")
        
        ttk.Radiobutton(dialog, text="Auto-detect", 
                       variable=model_var, value="auto").pack(pady=5)
        ttk.Radiobutton(dialog, text="Pico (RP2040)", 
                       variable=model_var, value="rp2040").pack(pady=5)
        ttk.Radiobutton(dialog, text="Pico 2 (RP2350)", 
                       variable=model_var, value="rp2350").pack(pady=5)
        
        def do_flash():
            dialog.destroy()
            model = model_var.get()
            
            # Determine firmware URL
            if model == "auto":
                if self.pico_model == "RP2350":
                    url = "https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
                else:
                    url = "https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2"
            elif model == "rp2040":
                url = "https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2"
            else:
                url = "https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
            
            # Download and flash in background
            threading.Thread(target=self.download_and_flash, 
                           args=(url,), daemon=True).start()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Flash", command=do_flash).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Text(dialog, height=5, width=50, wrap=tk.WORD)
        instructions.pack(pady=10, padx=10)
        instructions.insert('1.0', "Instructions:\n"
                                  "1. Click 'Flash' to download firmware\n"
                                  "2. When prompted, disconnect Pico\n"
                                  "3. Hold BOOTSEL and reconnect\n"
                                  "4. Firmware will be flashed automatically")
        instructions.config(state=tk.DISABLED)
    
    def download_and_flash(self, url):
        """Download and flash firmware"""
        self.operation_label.config(text="Downloading firmware...")
        self.progress_bar.start()
        
        try:
            # Download firmware
            filename = url.split('/')[-1]
            self.log(f"Downloading {filename}...", "INFO")
            
            import urllib.request
            urllib.request.urlretrieve(url, filename)
            self.log(f"Downloaded {filename}", "SUCCESS")
            
            # Prompt for BOOTSEL mode
            self.root.after(0, lambda: messagebox.showinfo(
                "Enter BOOTSEL Mode",
                "1. Disconnect your Pico\n"
                "2. Hold the BOOTSEL button\n"
                "3. Reconnect while holding BOOTSEL\n"
                "4. Release after 2 seconds\n\n"
                "Click OK when ready"))
            
            # Wait for BOOTSEL drive
            self.operation_label.config(text="Waiting for BOOTSEL mode...")
            bootsel_drive = self.wait_for_bootsel()
            
            if bootsel_drive:
                # Copy firmware
                self.operation_label.config(text="Flashing firmware...")
                import shutil
                shutil.copy2(filename, bootsel_drive)
                self.log("Firmware flashed successfully!", "SUCCESS")
                
                # Clean up
                os.remove(filename)
                
                messagebox.showinfo("Success", 
                                  "Firmware flashed! Pico will reboot automatically.")
            else:
                self.log("Could not find BOOTSEL drive", "ERROR")
                messagebox.showerror("Error", "Could not detect Pico in BOOTSEL mode")
                
        except Exception as e:
            self.log(f"Flash error: {e}", "ERROR")
            messagebox.showerror("Error", f"Failed to flash firmware: {e}")
        finally:
            self.progress_bar.stop()
            self.operation_label.config(text="Idle")
    
    def wait_for_bootsel(self):
        """Wait for Pico to appear in BOOTSEL mode"""
        for _ in range(60):  # Wait up to 60 seconds
            # Check for RPI-RP2 drive on Windows
            for drive_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{drive_letter}:\\"
                if os.path.exists(drive):
                    info_file = os.path.join(drive, "INFO_UF2.TXT")
                    if os.path.exists(info_file):
                        self.log(f"Found BOOTSEL drive at {drive}", "INFO")
                        return drive
            
            # Check for mounted drives on Linux/Mac
            for mount in ['/media', '/mnt', '/Volumes']:
                if os.path.exists(mount):
                    for folder in os.listdir(mount):
                        path = os.path.join(mount, folder)
                        info_file = os.path.join(path, "INFO_UF2.TXT")
                        if os.path.exists(info_file):
                            self.log(f"Found BOOTSEL drive at {path}", "INFO")
                            return path
            
            time.sleep(1)
        
        return None
    
    def wipe_pico(self):
        """Wipe all files from Pico"""
        if messagebox.askyesno("Confirm Wipe", 
                             "This will delete ALL files from the Pico.\n\n"
                             "Are you sure?"):
            self.operation_label.config(text="Wiping Pico...")
            self.progress_bar.start()
            
            def do_wipe():
                try:
                    result = subprocess.run(['mpremote', 'connect', 'auto', 
                                          'exec', 'import os; '
                                          '[os.remove(f) for f in os.listdir() '
                                          'if os.stat(f)[0] & 0x8000]'],
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.log("Pico wiped successfully", "SUCCESS")
                        self.root.after(0, self.refresh_files)
                    else:
                        self.log(f"Wipe failed: {result.stderr}", "ERROR")
                        
                except Exception as e:
                    self.log(f"Wipe error: {e}", "ERROR")
                finally:
                    self.root.after(0, self.progress_bar.stop)
                    self.root.after(0, lambda: self.operation_label.config(text="Idle"))
            
            threading.Thread(target=do_wipe, daemon=True).start()
    
    def reset_pico(self):
        """Reset the Pico"""
        try:
            subprocess.run(['mpremote', 'connect', 'auto', 'reset'],
                         check=True, capture_output=True)
            self.log("Pico reset", "INFO")
        except subprocess.CalledProcessError as e:
            self.log(f"Reset failed: {e}", "ERROR")
    
    def refresh_files(self):
        """Refresh both local and Pico file lists"""
        self.refresh_local_files()
        self.refresh_pico_files()
    
    def refresh_local_files(self):
        """Refresh local file list"""
        self.local_tree.delete(*self.local_tree.get_children())
        
        if not self.dir_var.get():
            return
        
        try:
            path = Path(self.dir_var.get())
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                if item.is_file() and item.suffix == '.py':
                    size = f"{item.stat().st_size} bytes"
                    modified = datetime.fromtimestamp(
                        item.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    
                    self.local_tree.insert('', 'end', text=item.name,
                                         values=(size, modified))
        except Exception as e:
            self.log(f"Error refreshing local files: {e}", "ERROR")
    
    def refresh_pico_files(self):
        """Refresh Pico file list"""
        if not self.pico_connected:
            return
        
        self.pico_tree.delete(*self.pico_tree.get_children())
        
        def do_refresh():
            try:
                result = subprocess.run(['mpremote', 'connect', 'auto', 'ls'],
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Parse ls output
                    for line in result.stdout.strip().split('\n'):
                        if line and not line.startswith('ls'):
                            parts = line.split()
                            if len(parts) >= 2:
                                size = parts[0]
                                name = ' '.join(parts[1:])
                                
                                self.root.after(0, lambda n=name, s=size: 
                                              self.pico_tree.insert('', 'end', 
                                                                  text=n, values=(s,)))
            except Exception as e:
                self.log(f"Error refreshing Pico files: {e}", "ERROR")
        
        threading.Thread(target=do_refresh, daemon=True).start()
    
    def upload_selected(self):
        """Upload selected local files to Pico"""
        selected = self.local_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select files to upload")
            return
        
        for item in selected:
            filename = self.local_tree.item(item)['text']
            filepath = os.path.join(self.dir_var.get(), filename)
            self.sync_queue.put(('file', filepath))
    
    def delete_selected(self):
        """Delete selected files from Pico"""
        selected = self.pico_tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select files to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Delete {len(selected)} file(s) from Pico?"):
            for item in selected:
                filename = self.pico_tree.item(item)['text']
                try:
                    subprocess.run(['mpremote', 'connect', 'auto', 'rm', 
                                  f':{filename}'], check=True, capture_output=True)
                    self.log(f"Deleted: {filename}", "INFO")
                except subprocess.CalledProcessError as e:
                    self.log(f"Failed to delete {filename}: {e}", "ERROR")
            
            self.refresh_pico_files()
    
    def save_settings(self):
        """Save settings from settings tab"""
        self.save_config()
        messagebox.showinfo("Settings Saved", "Settings have been saved")
        
        # Restart file watching if needed
        if self.pico_connected and self.auto_sync_enabled.get():
            self.stop_file_watching()
            self.start_file_watching()
    
    def clear_log(self):
        """Clear log display"""
        self.log_text.delete('1.0', tk.END)
    
    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        
        if filename:
            with open(filename, 'w') as f:
                f.write(self.log_text.get('1.0', tk.END))
            messagebox.showinfo("Log Saved", f"Log saved to {filename}")
    
    def log(self, message, level="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Queue log entry for thread-safe display
        self.log_queue.put(log_entry)
        
        # Also write to file
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(log_entry)
        except:
            pass
    
    def process_logs(self):
        """Process log queue and update display"""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
                
                # Limit log size
                if int(self.log_text.index('end-1c').split('.')[0]) > 1000:
                    self.log_text.delete('1.0', '100.0')
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_logs)
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_file_watching()
        self.save_config()
        self.root.destroy()

def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set DPI awareness on Windows
    if platform.system() == 'Windows':
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    app = PicoSyncManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
