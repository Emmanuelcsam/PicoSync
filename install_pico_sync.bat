@echo off
REM install_pico_sync.bat - Quick installer for Pico Sync Manager
title Pico Sync Manager Installer

echo ============================================
echo    Pico Sync Manager - Quick Installer
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if files exist
if not exist "pico_sync_manager.py" (
    echo [ERROR] pico_sync_manager.py not found!
    echo Please extract all files to the same directory
    pause
    exit /b 1
)

echo Installing required packages...
echo.

REM Install requirements
pip install mpremote pyserial watchdog >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Some packages may have failed to install
    echo Trying alternative method...
    python -m pip install mpremote pyserial watchdog
)

echo [OK] Dependencies installed
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop

REM Create VBS script for shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP%\Pico Sync Manager.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "pythonw.exe" >> CreateShortcut.vbs
echo oLink.Arguments = """%CD%\pico_sync_manager.py""" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.IconLocation = "pythonw.exe, 0" >> CreateShortcut.vbs
echo oLink.Description = "Pico Sync Manager - Automated Pico Development Tool" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs >nul
del CreateShortcut.vbs

if exist "%DESKTOP%\Pico Sync Manager.lnk" (
    echo [OK] Desktop shortcut created
) else (
    echo [WARNING] Could not create desktop shortcut
)

echo.
echo ============================================
echo    Installation Complete!
echo ============================================
echo.
echo You can now run Pico Sync Manager by:
echo 1. Double-clicking the desktop shortcut
echo 2. Running: python pico_sync_manager.py
echo 3. Using: run_pico_sync.bat
echo.
echo Would you like to start Pico Sync Manager now?
choice /C YN /M "Start now"

if errorlevel 2 goto end
if errorlevel 1 goto start

:start
echo.
echo Starting Pico Sync Manager...
start pythonw pico_sync_manager.py
goto end

:end
echo.
echo Setup complete. Press any key to exit...
pause >nul