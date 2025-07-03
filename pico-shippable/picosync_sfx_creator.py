#!/usr/bin/env python3
"""
Create Self-Extracting Archive for PicoSync
This creates a single executable that contains everything needed
"""

import os
import sys
import base64
import zlib
import json
from pathlib import Path

def create_sfx_installer():
    """Create self-extracting installer script"""
    
    # This is the template for the self-extracting executable
    sfx_template = '''#!/usr/bin/env python3
"""
PicoSync Self-Extracting Installer
Single file that contains and installs everything
"""

import os
import sys
import base64
import zlib
import tempfile
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Embedded archive (will be replaced with actual data)
ARCHIVE_DATA = "{ARCHIVE_DATA}"

class SelfExtractor:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.install_dir = Path.home() / "PicoSync"
        
    def extract(self):
        """Extract embedded archive"""
        print("Extracting files...")
        
        # Decode and decompress archive
        archive_bytes = base64.b64decode(ARCHIVE_DATA)
        decompressed = zlib.decompress(archive_bytes)
        
        # Write to temp file
        archive_path = self.temp_dir / "picosync.zip"
        with open(archive_path, "wb") as f:
            f.write(decompressed)
        
        # Extract zip
        import zipfile
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(self.temp_dir)
        
        return True
    
    def install(self):
        """Run installation"""
        print("Installing PicoSync...")
        
        # Create install directory
        self.install_dir.mkdir(exist_ok=True)
        
        # Copy files
        src_dir = self.temp_dir / "PicoSync"
        if src_dir.exists():
            shutil.copytree(src_dir, self.install_dir, dirs_exist_ok=True)
        else:
            # Files might be directly in temp_dir
            for item in self.temp_dir.iterdir():
                if item.name != "picosync.zip":
                    dest = self.install_dir / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)
        
        # Run post-install setup
        setup_script = self.install_dir / "setup.py"
        if setup_script.exists():
            subprocess.run([sys.executable, str(setup_script)], 
                         cwd=str(self.install_dir))
        
        # Create shortcuts
        self.create_shortcuts()
        
        print("Installation complete!")
        return True
    
    def create_shortcuts(self):
        """Create desktop shortcuts"""
        desktop = Path.home() / "Desktop"
        
        if sys.platform == "win32":
            # Windows shortcut
            shortcut_path = desktop / "PicoSync.lnk"
            target = self.install_dir / "PicoSync.exe"
            
            if not target.exists():
                target = self.install_dir / "run.bat"
            
            if target.exists():
                # Create shortcut using PowerShell
                ps_script = f"""
                $WshShell = New-Object -ComObject WScript.Shell
                $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
                $Shortcut.TargetPath = "{target}"
                $Shortcut.WorkingDirectory = "{self.install_dir}"
                $Shortcut.IconLocation = "{self.install_dir}\\icon.ico,0"
                $Shortcut.Save()
                """
                
                subprocess.run(["powershell", "-Command", ps_script])
        
        elif sys.platform == "linux":
            # Linux desktop entry
            desktop_entry = f"""[Desktop Entry]
Name=PicoSync
Comment=Raspberry Pi Pico Development Tool
Exec={self.install_dir}/run.sh
Icon={self.install_dir}/icon.png
Terminal=false
Type=Application
Categories=Development;
"""
            desktop_file = Path.home() / ".local/share/applications/picosync.desktop"
            desktop_file.parent.mkdir(parents=True, exist_ok=True)
            desktop_file.write_text(desktop_entry)
    
    def cleanup(self):
        """Clean up temp files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def run(self):
        """Run extraction and installation"""
        try:
            # Show GUI
            root = tk.Tk()
            root.withdraw()
            
            result = messagebox.askyesno(
                "PicoSync Installer",
                "This will install PicoSync on your computer.\\n\\n"
                "Installation directory:\\n"
                f"{self.install_dir}\\n\\n"
                "Continue with installation?"
            )
            
            if not result:
                print("Installation cancelled.")
                return
            
            root.destroy()
            
            # Extract and install
            if self.extract() and self.install():
                # Show completion dialog
                root = tk.Tk()
                root.withdraw()
                
                launch = messagebox.askyesno(
                    "Installation Complete",
                    "PicoSync has been installed successfully!\\n\\n"
                    "Would you like to launch it now?"
                )
                
                if launch:
                    # Launch the app
                    if sys.platform == "win32":
                        os.startfile(self.install_dir / "PicoSync.exe")
                    else:
                        subprocess.Popen([str(self.install_dir / "run.sh")])
                
                root.destroy()
            
        except Exception as e:
            messagebox.showerror("Installation Error", f"An error occurred:\\n{str(e)}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    extractor = SelfExtractor()
    extractor.run()
'''
    
    # Read all files and create archive
    print("Creating self-extracting archive...")
    
    # Create a temporary directory structure
    temp_dir = Path("temp_build")
    temp_dir.mkdir(exist_ok=True)
    
    picosync_dir = temp_dir / "PicoSync"
    picosync_dir.mkdir(exist_ok=True)
    
    # Copy all necessary files
    files_to_include = [
        "pico_sync_manager.py",
        "install_picosync.py", 
        "run_picosync.py",
        "config/core/requirements.txt",
        "config/core/run.ico",
        "config/core/install.ico"
    ]
    
    for file_path in files_to_include:
        src = Path(file_path)
        if src.exists():
            dest = picosync_dir / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    
    # Create setup script
    setup_content = '''#!/usr/bin/env python3
"""Post-installation setup for PicoSync"""

import subprocess
import sys
import os
from pathlib import Path

def setup():
    """Run post-installation setup"""
    print("Running post-installation setup...")
    
    # Create virtual environment
    venv_path = Path.cwd() / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)])
    
    # Install dependencies
    if sys.platform == "win32":
        pip = venv_path / "Scripts" / "pip.exe"
    else:
        pip = venv_path / "bin" / "pip"
    
    req_file = Path.cwd() / "config" / "core" / "requirements.txt"
    if req_file.exists():
        subprocess.run([str(pip), "install", "-r", str(req_file)])
    
    # Create run scripts
    if sys.platform == "win32":
        run_bat = Path.cwd() / "run.bat"
        run_bat.write_text("""@echo off
cd /d "%~dp0"
call venv\\Scripts\\activate
python pico_sync_manager.py
pause
""")
    else:
        run_sh = Path.cwd() / "run.sh"
        run_sh.write_text("""#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python pico_sync_manager.py
""")
        run_sh.chmod(0o755)
    
    print("Setup complete!")

if __name__ == "__main__":
    setup()
'''
    
    with open(picosync_dir / "setup.py", "w") as f:
        f.write(setup_content)
    
    # Create zip archive
    import zipfile
    archive_path = temp_dir / "picosync.zip"
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(picosync_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zf.write(file_path, arcname)
    
    # Read archive and encode
    with open(archive_path, "rb") as f:
        archive_data = f.read()
    
    compressed = zlib.compress(archive_data, 9)
    encoded = base64.b64encode(compressed).decode()
    
    # Create final SFX script
    sfx_content = sfx_template.replace("{ARCHIVE_DATA}", encoded)
    
    with open("PicoSync_Installer.py", "w") as f:
        f.write(sfx_content)
    
    print("Created: PicoSync_Installer.py")
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    # Create PyInstaller spec for the SFX
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['PicoSync_Installer.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['zipfile', 'zlib', 'base64', 'tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PicoSync_Setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='config/core/install.ico' if os.path.exists('config/core/install.ico') else None,
)
'''
    
    with open("sfx_installer.spec", "w") as f:
        f.write(spec_content)
    
    print("Created: sfx_installer.spec")
    print("\nTo create executable:")
    print("1. Install PyInstaller: pip install pyinstaller")
    print("2. Run: pyinstaller --clean sfx_installer.spec")
    print("3. Find executable in: dist/PicoSync_Setup.exe")

if __name__ == "__main__":
    create_sfx_installer()
