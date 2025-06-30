# 🚀 Quick Start - Solving "Python not in PATH"

## Option 1: Use the Smart Launcher (Easiest)

1. **Run `PicoSync_SmartLauncher.bat`**
   - It will detect if Python is installed
   - Offers automatic fixes if Python is found
   - Guides you through installation if needed

## Option 2: Quick Microsoft Store Install

1. **Open Command Prompt and type:**
   ```
   python
   ```
2. **Windows will open Microsoft Store automatically**
3. **Click "Get" to install Python**
4. **Run the installer again**

## Option 3: Manual Python Install

1. **Download Python:**
   - Go to https://www.python.org/downloads/
   - Download Python 3.11.x (recommended)

2. **Install with PATH:**
   - Run the installer
   - ✅ **CHECK "Add Python to PATH"** (bottom of first screen)
   - Click "Install Now"

3. **Verify Installation:**
   - Open NEW Command Prompt
   - Type: `python --version`
   - Should show: `Python 3.11.x`

## Option 4: Use PowerShell Installer

1. **Right-click `install_pico_sync.ps1`**
2. **Select "Run with PowerShell"**
3. **Follow the prompts**

## Option 5: Quick Fix (Temporary)

If Python is installed but not in PATH:

1. **Find your Python location:**
   - Usually in: `C:\Users\[YourName]\AppData\Local\Programs\Python\Python311\`

2. **Create a batch file** in the same folder as `pico_sync_manager.py`:
   ```batch
   @echo off
   "C:\Users\[YourName]\AppData\Local\Programs\Python\Python311\python.exe" pico_sync_manager.py
   pause
   ```

3. **Save as `RunPicoSync.bat`** and double-click to run

## 🆘 Still Having Issues?

### Common Locations for Python:
- `C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\`
- `C:\Python311\`
- `C:\Program Files\Python311\`

### Check if Python is installed:
1. Open File Explorer
2. Go to one of the above locations
3. Look for `python.exe`

### If found, add to PATH manually:
1. Press `Win + X` → "System"
2. "Advanced system settings"
3. "Environment Variables"
4. Edit "Path" under System variables
5. Add the Python folder path
6. Add the Python\Scripts folder path
7. Click OK and restart Command Prompt

## 🎯 Fastest Solution

**Just run these in order:**

1. `PicoSync_SmartLauncher.bat` - Tries everything automatically
2. `enhanced_installer.bat` - More detection options
3. `fix_python_path.bat` - Helps fix PATH issues

One of these will work!