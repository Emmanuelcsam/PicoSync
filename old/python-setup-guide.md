# Python Setup Guide for Pico Sync Manager

## 🔧 Fixing "Python is not installed or not in PATH"

### Option 1: Install Python (Recommended)

1. **Download Python**
   - Go to https://www.python.org/downloads/
   - Download Python 3.9 or newer (avoid 3.12 if it causes issues)
   - **Important**: Download the 64-bit version

2. **Install Python with PATH**
   - Run the installer
   - ⚠️ **CRITICAL**: Check ✅ "Add Python to PATH" at the bottom of the first screen
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation**
   - Open a NEW Command Prompt (cmd)
   - Type: `python --version`
   - You should see: `Python 3.x.x`

### Option 2: Fix Existing Python Installation

If Python is installed but not in PATH:

1. **Find Python Location**
   - Common locations:
     - `C:\Python39\`
     - `C:\Python310\`
     - `C:\Users\[YourName]\AppData\Local\Programs\Python\Python39\`

2. **Add to PATH Manually**
   - Press `Win + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find and select "Path"
   - Click "Edit"
   - Click "New" and add:
     - `C:\Python39\` (or your Python location)
     - `C:\Python39\Scripts\`
   - Click "OK" on all windows

3. **Restart Command Prompt**
   - Close all Command Prompt windows
   - Open a new one and test: `python --version`

### Option 3: Use Python from Microsoft Store

1. Open Microsoft Store
2. Search for "Python 3.9" or "Python 3.10"
3. Click "Get" to install
4. This automatically adds Python to PATH

## 🚀 Quick Test

After installing Python, test it:

```batch
python --version
pip --version
```

Both commands should work without errors.

## 🎯 Next Steps

Once Python is working:
1. Run `install_pico_sync.bat` again
2. Or use the standalone launcher below

## ⚡ Alternative: PowerShell Installer

If you're still having issues, try this PowerShell command:

```powershell
# Run this in PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco install python3 -y
refreshenv
```

## 🆘 Still Having Issues?

Common problems and solutions:

1. **"python" not recognized but "python3" works**
   - Use `python3` instead of `python` in scripts
   - Or create an alias: `doskey python=python3`

2. **Multiple Python versions**
   - Use Python Launcher: `py -3 --version`
   - Specify version: `py -3.9 script.py`

3. **Permission errors**
   - Run Command Prompt as Administrator
   - Or install Python for current user only

4. **Antivirus blocking Python**
   - Add Python folder to antivirus exceptions
   - Temporarily disable antivirus during installation