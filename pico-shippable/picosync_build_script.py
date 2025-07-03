#!/usr/bin/env python3
"""
PicoSync Build Script
Creates standalone executables and installer for distribution
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import zipfile
import platform

class PicoSyncBuilder:
    def __init__(self):
        self.base_dir = Path(__file__).parent.resolve()
        self.build_dir = self.base_dir / "build"
        self.dist_dir = self.base_dir / "dist"
        self.output_dir = self.base_dir / "release"
        self.system = platform.system()
        
    def clean_build_dirs(self):
        """Clean previous build directories"""
        print("Cleaning previous builds...")
        for dir_path in [self.build_dir, self.dist_dir, self.output_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        
    def install_build_deps(self):
        """Install PyInstaller and other build dependencies"""
        print("Installing build dependencies...")
        deps = ["pyinstaller", "pillow"]  # Pillow for icon handling
        
        for dep in deps:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    def create_pyinstaller_specs(self):
        """Create PyInstaller spec files"""
        print("Creating PyInstaller spec files...")
        
        # Main application spec
        main_spec = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pico_sync_manager.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/core/*.ico', 'config/core'),
        ('config/core/*.png', 'config/core'),
    ],
    hiddenimports=[
        'tkinter',
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'mpremote',
        'mpremote.main',
        'mpremote.pyboard',
        'mpremote.transport',
        'mpremote.transport_serial',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PicoSync',
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
    icon='config/core/run.ico' if sys.platform == 'win32' else None,
)
'''
        
        # Installer spec
        installer_spec = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['install_picosync.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/core/*.ico', 'config/core'),
        ('pico_sync_manager.py', '.'),
        ('run_picosync.py', '.'),
        ('config/core/requirements.txt', 'config/core'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PicoSync_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='config/core/install.ico' if sys.platform == 'win32' else None,
)
'''
        
        with open("picosync.spec", "w") as f:
            f.write(main_spec)
            
        with open("installer.spec", "w") as f:
            f.write(installer_spec)
    
    def build_executables(self):
        """Build executables with PyInstaller"""
        print("Building executables...")
        
        # Build main application
        subprocess.run(["pyinstaller", "--clean", "picosync.spec"], check=True)
        
        # Build installer  
        subprocess.run(["pyinstaller", "--clean", "installer.spec"], check=True)
    
    def create_portable_package(self):
        """Create portable package with all files"""
        print("Creating portable package...")
        
        self.output_dir.mkdir(exist_ok=True)
        package_dir = self.output_dir / "PicoSync_Portable"
        package_dir.mkdir(exist_ok=True)
        
        # Copy executables
        if self.system == "Windows":
            shutil.copy2(self.dist_dir / "PicoSync.exe", package_dir)
            shutil.copy2(self.dist_dir / "PicoSync_Installer.exe", package_dir)
        else:
            shutil.copy2(self.dist_dir / "PicoSync", package_dir)
            shutil.copy2(self.dist_dir / "PicoSync_Installer", package_dir)
        
        # Copy config directory structure
        config_dir = package_dir / "config" / "core"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy icons and requirements
        for file in ["run.ico", "install.ico", "requirements.txt"]:
            src = self.base_dir / "config" / "core" / file
            if src.exists():
                shutil.copy2(src, config_dir)
        
        # Copy Python files for installer to use
        for file in ["pico_sync_manager.py", "run_picosync.py", "install_picosync.py"]:
            src = self.base_dir / file
            if src.exists():
                shutil.copy2(src, package_dir)
        
        # Create README
        readme_content = """PicoSync - Raspberry Pi Pico Development Tool
============================================

Quick Start:
1. Run PicoSync_Installer.exe to set up the environment
2. Run PicoSync.exe to start the application

Features:
- Automatic file synchronization
- Firmware flashing support
- File management
- Support for both Pico (RP2040) and Pico 2 (RP2350)

Requirements:
- Windows 10/11 (64-bit)
- USB drivers for Raspberry Pi Pico
- Internet connection for initial setup

First Run:
1. The installer will download and set up Python dependencies
2. Select a directory to sync with your Pico
3. Connect your Pico via USB
4. Enable Auto Sync for automatic file updates

For more information, visit: https://github.com/yourusername/picosync
"""
        
        with open(package_dir / "README.txt", "w") as f:
            f.write(readme_content)
        
        # Create batch files for easy launching
        if self.system == "Windows":
            with open(package_dir / "Install.bat", "w") as f:
                f.write("@echo off\nstart PicoSync_Installer.exe\n")
                
            with open(package_dir / "Run.bat", "w") as f:
                f.write("@echo off\nstart PicoSync.exe\n")
    
    def create_installer_script(self):
        """Create Inno Setup script for Windows installer"""
        if self.system != "Windows":
            print("Skipping Inno Setup script (Windows only)")
            return
            
        print("Creating Inno Setup script...")
        
        inno_script = """[Setup]
AppName=PicoSync
AppVersion=1.0.0
AppPublisher=Your Company
AppPublisherURL=https://github.com/yourusername/picosync
AppSupportURL=https://github.com/yourusername/picosync/issues
DefaultDirName={autopf}\\PicoSync
DefaultGroupName=PicoSync
AllowNoIcons=yes
OutputDir=release
OutputBaseFilename=PicoSync_Setup_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\PicoSync.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\\PicoSync_Installer.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config\\core\\*"; DestDir: "{app}\\config\\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "pico_sync_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "run_picosync.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "install_picosync.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\\PicoSync"; Filename: "{app}\\PicoSync.exe"
Name: "{group}\\PicoSync Installer"; Filename: "{app}\\PicoSync_Installer.exe"
Name: "{group}\\{cm:UninstallProgram,PicoSync}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\PicoSync"; Filename: "{app}\\PicoSync.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\PicoSync_Installer.exe"; Description: "Run initial setup"; Flags: nowait postinstall skipifsilent
"""
        
        with open("picosync_setup.iss", "w") as f:
            f.write(inno_script)
        
        print("Inno Setup script created: picosync_setup.iss")
        print("To create installer, run: iscc picosync_setup.iss")
    
    def create_zip_package(self):
        """Create ZIP package for distribution"""
        print("Creating ZIP package...")
        
        package_dir = self.output_dir / "PicoSync_Portable"
        zip_path = self.output_dir / f"PicoSync_Portable_{self.system}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Created: {zip_path}")
    
    def build_all(self):
        """Run complete build process"""
        print("Starting PicoSync build process...")
        print(f"Platform: {self.system}")
        
        self.clean_build_dirs()
        self.install_build_deps()
        self.create_pyinstaller_specs()
        self.build_executables()
        self.create_portable_package()
        self.create_installer_script()
        self.create_zip_package()
        
        print("\nBuild complete!")
        print(f"Output files in: {self.output_dir}")
        
        if self.system == "Windows":
            print("\nNext steps:")
            print("1. Install Inno Setup from https://jrsoftware.org/isinfo.php")
            print("2. Run: iscc picosync_setup.iss")
            print("3. Find installer in release/PicoSync_Setup_v1.0.0.exe")

if __name__ == "__main__":
    builder = PicoSyncBuilder()
    builder.build_all()
