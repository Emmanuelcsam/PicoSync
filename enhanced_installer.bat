@echo off
REM enhanced_installer.bat - Improved installer with better Python detection
setlocal enabledelayedexpansion
title Pico Sync Manager - Enhanced Installer

echo ============================================
echo    Pico Sync Manager - Enhanced Installer
echo ============================================
echo.

REM Try different Python commands
set PYTHON_CMD=
set PYTHON_FOUND=0

REM Check python
python --version >nul 2>&1
if !errorlevel! == 0 (
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    echo [OK] Found Python as 'python'
    goto :python_found
)

REM Check python3
python3 --version >nul 2>&1
if !errorlevel! == 0 (
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    echo [OK] Found Python as 'python3'
    goto :python_found
)

REM Check py launcher
py --version >nul 2>&1
if !errorlevel! == 0 (
    set PYTHON_CMD=py
    set PYTHON_FOUND=1
    echo [OK] Found Python via 'py' launcher
    goto :python_found
)

REM Check common Python locations
for %%p in (
    "C:\Python39\python.exe"
    "C:\Python310\python.exe"
    "C:\Python311\python.exe"
    "C:\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) do (
    if exist %%p (
        set PYTHON_CMD=%%p
        set PYTHON_FOUND=1
        echo [OK] Found Python at: %%p
        goto :python_found
    )
)

:python_not_found
echo [ERROR] Python is not installed or not found!
echo.
echo ============================================
echo    Python Installation Required
echo ============================================
echo.
echo Please install Python using ONE of these methods:
echo.
echo METHOD 1 - Download from Python.org (Recommended):
echo   1. Visit: https://www.python.org/downloads/
echo   2. Download Python 3.9 or newer
echo   3. Run installer and CHECK "Add Python to PATH"
echo   4. Click "Install Now"
echo.
echo METHOD 2 - Microsoft Store (Easiest):
echo   1. Open Microsoft Store
echo   2. Search for "Python 3.10"
echo   3. Click "Get" to install
echo.
echo METHOD 3 - If Python is installed but not in PATH:
echo   Run this command to see instructions:
echo   notepad python_setup_guide.md
echo.
echo ============================================
echo.
echo Press any key to open Python download page...
pause >nul
start https://www.python.org/downloads/
goto :end

:python_found
echo.
echo Python executable: !PYTHON_CMD!
!PYTHON_CMD! --version
echo.

REM Check if main script exists
if not exist "pico_sync_manager.py" (
    echo [ERROR] pico_sync_manager.py not found!
    echo Please ensure all files are extracted to the same directory
    pause
    goto :end
)

echo Installing required packages...
echo.

REM Create requirements file if it doesn't exist
if not exist "requirements.txt" (
    echo Creating requirements.txt...
    (
        echo mpremote
        echo pyserial
        echo watchdog
    ) > requirements.txt
)

REM Install packages
echo Installing: mpremote, pyserial, watchdog
echo Please wait...
echo.

!PYTHON_CMD! -m pip install --upgrade pip >nul 2>&1
!PYTHON_CMD! -m pip install -r requirements.txt

if !errorlevel! neq 0 (
    echo [WARNING] Some packages may have failed to install
    echo Trying alternative method...
    !PYTHON_CMD! -m pip install mpremote pyserial watchdog
)

REM Verify installation
echo.
echo Verifying installation...
!PYTHON_CMD! -c "import mpremote, serial, watchdog; print('[OK] All packages installed successfully')" 2>nul
if !errorlevel! neq 0 (
    echo [WARNING] Some packages may not be properly installed
    echo The application will try to install them on first run
) else (
    echo.
)

REM Create launchers
echo Creating launcher scripts...

REM Create Python-specific launcher
(
    echo @echo off
    echo title Pico Sync Manager
    echo echo Starting Pico Sync Manager...
    echo !PYTHON_CMD! pico_sync_manager.py
    echo if errorlevel 1 pause
) > run_pico_sync_custom.bat

echo [OK] Created run_pico_sync_custom.bat

REM Create desktop shortcut
echo.
echo Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop

REM Create VBS script for shortcut with proper Python path
(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%DESKTOP%\Pico Sync Manager.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "%CD%\run_pico_sync_custom.bat"
    echo oLink.WorkingDirectory = "%CD%"
    echo oLink.WindowStyle = 7
    echo oLink.Description = "Pico Sync Manager - Automated Pico Development Tool"
    echo oLink.Save
) > CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs

if exist "%DESKTOP%\Pico Sync Manager.lnk" (
    echo [OK] Desktop shortcut created
) else (
    echo [WARNING] Could not create desktop shortcut
)

REM Create Start Menu shortcut
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs
if not exist "%STARTMENU%\Pico Sync Manager" mkdir "%STARTMENU%\Pico Sync Manager"

(
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo sLinkFile = "%STARTMENU%\Pico Sync Manager\Pico Sync Manager.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "%CD%\run_pico_sync_custom.bat"
    echo oLink.WorkingDirectory = "%CD%"
    echo oLink.WindowStyle = 7
    echo oLink.Description = "Pico Sync Manager"
    echo oLink.Save
) > CreateStartMenu.vbs

cscript //nologo CreateStartMenu.vbs >nul 2>&1
del CreateStartMenu.vbs

echo.
echo ============================================
echo    Installation Complete!
echo ============================================
echo.
echo Pico Sync Manager has been installed with:
echo   - Desktop shortcut
echo   - Custom launcher (run_pico_sync_custom.bat)
echo   - All required dependencies
echo.
echo You can now run Pico Sync Manager by:
echo   1. Double-clicking the desktop shortcut
echo   2. Running: run_pico_sync_custom.bat
echo   3. Running: !PYTHON_CMD! pico_sync_manager.py
echo.
echo Would you like to start Pico Sync Manager now? (Y/N)
choice /C YN /T 10 /D Y >nul

if errorlevel 2 goto :skip_start
if errorlevel 1 goto :start_app

:start_app
echo.
echo Starting Pico Sync Manager...
start "" "%CD%\run_pico_sync_custom.bat"
goto :end

:skip_start
echo.
echo You can start Pico Sync Manager anytime using the desktop shortcut.

:end
echo.
echo Press any key to exit...
pause >nul
endlocal