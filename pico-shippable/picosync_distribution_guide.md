# PicoSync Distribution Guide

This guide explains how to create distributable versions of PicoSync that customers can easily install and run with just a double-click.

## Overview of Distribution Options

### 1. **Self-Extracting Executable (Recommended)**
- Single `.exe` file that contains everything
- Customer double-clicks to install
- No Python knowledge required
- Works on Windows, can be adapted for Linux/Mac

### 2. **Windows Installer (Professional)**
- Traditional `.msi` or Inno Setup installer
- Professional appearance
- Can add to Programs & Features
- Desktop and Start Menu shortcuts

### 3. **Portable ZIP Package**
- No installation required
- Extract and run
- Good for USB drives
- Cross-platform with platform-specific builds

## Step-by-Step Instructions

### Option 1: Create Self-Extracting Executable

1. **Prepare your environment:**
   ```bash
   pip install pyinstaller pillow
   ```

2. **Run the self-extracting archive creator:**
   ```bash
   python create_sfx_installer.py
   ```

3. **Build the executable:**
   ```bash
   pyinstaller --clean sfx_installer.spec
   ```

4. **Result:** `dist/PicoSync_Setup.exe` - Single file customers can double-click

### Option 2: Create Windows Installer

1. **Build executables first:**
   ```bash
   python build_picosync.py
   ```

2. **Install Inno Setup:**
   - Download from: https://jrsoftware.org/isdl.php
   - Install with default options

3. **Compile installer:**
   ```bash
   iscc picosync_setup.iss
   ```

4. **Result:** `release/PicoSync_Setup_v1.0.0.exe` - Professional installer

### Option 3: Create Portable Package

1. **Run the build script:**
   ```bash
   python build_picosync.py
   ```

2. **Find portable package:**
   - Location: `release/PicoSync_Portable_Windows.zip`
   - Contains everything needed to run

## Quick Start for Developers

If you want the simplest solution that creates a single executable file:

```bash
# 1. Install dependencies
pip install pyinstaller

# 2. Create simple one-file executable
pyinstaller --onefile --windowed --icon=config/core/run.ico --add-data "config/core/*:config/core" --name PicoSync pico_sync_manager.py

# Result: dist/PicoSync.exe
```

## Advanced: Multi-Platform Distribution

### For macOS:
```bash
# Create .app bundle
pyinstaller --onefile --windowed --icon=icon.icns --name PicoSync pico_sync_manager.py

# Create DMG
hdiutil create -volname "PicoSync" -srcfolder dist/PicoSync.app -ov -format UDZO PicoSync.dmg
```

### For Linux:
```bash
# Create AppImage
# First, build with pyinstaller
pyinstaller --onefile --name PicoSync pico_sync_manager.py

# Then use appimagetool to create AppImage
# (Requires additional setup)
```

## What Customers See

### Self-Extracting Executable:
1. Download `PicoSync_Setup.exe`
2. Double-click to run
3. Click "Install" in the dialog
4. PicoSync is installed with desktop shortcut
5. Double-click shortcut to run

### Windows Installer:
1. Download `PicoSync_Setup_v1.0.0.exe`
2. Run installer wizard
3. Choose install location
4. Installation creates Start Menu and optional desktop shortcuts
5. Launch from Start Menu or desktop

### Portable Package:
1. Download `PicoSync_Portable_Windows.zip`
2. Extract to any location (e.g., USB drive)
3. Run `PicoSync.exe` from extracted folder
4. No installation needed

## File Structure in Distribution

```
PicoSync/
├── PicoSync.exe          # Main application
├── config/
│   └── core/
│       ├── run.ico       # Application icon
│       ├── install.ico   # Installer icon
│       └── requirements.txt
├── README.txt            # User instructions
└── run.bat              # Batch file launcher (optional)
```

## Signing Your Executable (Optional)

For professional distribution, consider code signing:

```bash
# Windows (requires certificate)
signtool sign /a /t http://timestamp.digicert.com PicoSync_Setup.exe
```

## Testing Your Distribution

Before sending to customers:

1. **Test on clean system:**
   - Use fresh Windows VM
   - No Python installed
   - No development tools

2. **Verify all features work:**
   - USB detection
   - File sync
   - Firmware flashing
   - All UI elements

3. **Check antivirus:**
   - Some AV software flags unsigned Python executables
   - Consider code signing or whitelisting

## Troubleshooting Common Issues

### "Windows protected your PC" warning:
- This appears for unsigned executables
- Users click "More info" → "Run anyway"
- Or get a code signing certificate

### Missing DLL errors:
- Include Visual C++ Redistributable
- Or use `--onefile` option in PyInstaller

### Large file size:
- Use UPX compression: `pyinstaller --upx-dir=/path/to/upx`
- Exclude unnecessary modules

## Final Distribution Checklist

- [ ] Executable runs without Python installed
- [ ] All icons display correctly  
- [ ] Desktop/Start Menu shortcuts work
- [ ] No console window appears (for GUI app)
- [ ] File sync works with real Pico device
- [ ] Error messages are user-friendly
- [ ] README includes system requirements
- [ ] Version number is correct
- [ ] Tested on Windows 10 and 11

## System Requirements for End Users

Include this in your distribution:

**Minimum Requirements:**
- Windows 10/11 (64-bit)
- 100MB free disk space
- USB 2.0 port
- Internet connection (for initial setup)

**Recommended:**
- Windows 11
- 500MB free disk space  
- USB 3.0 port
- Raspberry Pi Pico USB drivers installed