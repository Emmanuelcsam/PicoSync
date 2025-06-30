#!/usr/bin/env python3
"""
build_executable.py - Build standalone executable for Pico Sync Manager
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_requirements():
    """Check and install required packages"""
    print("Checking requirements...")
    
    required = ['pyinstaller', 'mpremote', 'pyserial', 'watchdog']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        for package in missing:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print("Dependencies installed!")
    else:
        print("All dependencies satisfied!")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable file
        '--windowed',  # No console window
        '--name', 'PicoSyncManager',
        '--icon', 'NONE',  # You can add an icon file here
        '--add-data', 'pico_sync_manager.py;.',  # Include the main script
        '--hidden-import', 'serial.tools.list_ports',
        '--hidden-import', 'watchdog.observers',
        '--hidden-import', 'watchdog.events',
        '--clean',  # Clean temporary files
        'pico_sync_manager.py'
    ]
    
    # Remove --icon if on non-Windows
    if sys.platform != 'win32':
        cmd.remove('--icon')
        cmd.remove('NONE')
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful!")
        
        # Find the executable
        if sys.platform == 'win32':
            exe_path = Path('dist/PicoSyncManager.exe')
        else:
            exe_path = Path('dist/PicoSyncManager')
        
        if exe_path.exists():
            print(f"Executable created at: {exe_path.absolute()}")
            
            # Copy to current directory
            shutil.copy2(exe_path, '.')
            print(f"Copied to: {Path('.').absolute() / exe_path.name}")
            
            # Create a shortcut batch file for Windows
            if sys.platform == 'win32':
                with open('PicoSync.bat', 'w') as f:
                    f.write('@echo off\n')
                    f.write('start "" "PicoSyncManager.exe"\n')
                print("Created PicoSync.bat shortcut")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    return True

def create_requirements_file():
    """Create requirements.txt for easy installation"""
    requirements = [
        'mpremote',
        'pyserial',
        'watchdog',
        'pyinstaller'
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    print("Created requirements.txt")

def main():
    print("Pico Sync Manager - Executable Builder")
    print("=" * 40)
    
    # Check if main script exists
    if not Path('pico_sync_manager.py').exists():
        print("ERROR: pico_sync_manager.py not found!")
        print("Please ensure the main script is in the current directory")
        input("\nPress Enter to exit...")
        return
    
    # Create requirements file
    create_requirements_file()
    
    # Check and install requirements
    check_requirements()
    
    # Build executable
    print("\nReady to build executable.")
    response = input("Continue? (y/n): ")
    
    if response.lower() == 'y':
        if build_executable():
            print("\n" + "=" * 40)
            print("BUILD COMPLETE!")
            print("\nYou can now:")
            print("1. Run PicoSyncManager.exe directly")
            print("2. Double-click PicoSync.bat")
            print("3. Create a desktop shortcut to either file")
            print("\nThe executable includes all dependencies.")
            print("No Python installation required on target machine!")
        else:
            print("\nBuild failed. Please check the error messages above.")
    else:
        print("Build cancelled.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
