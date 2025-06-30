@echo off
REM PicoSync_SmartLauncher.bat - All-in-one launcher with Python detection and fixes
setlocal enabledelayedexpansion
title Pico Sync Manager - Smart Launcher

REM Try to find Python
set PYTHON_CMD=
set PYTHON_FOUND=0

REM Quick check for common commands
for %%c in (python python3 py) do (
    %%c --version >nul 2>&1
    if !errorlevel! == 0 (
        set PYTHON_CMD=%%c
        set PYTHON_FOUND=1
        goto :found_python
    )
)

REM Check common installation paths
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
) do (
    if exist %%p (
        set PYTHON_CMD=%%p
        set PYTHON_FOUND=1
        goto :found_python
    )
)

REM Python not found - offer solutions
:python_not_found
cls
echo ============================================
echo    Pico Sync Manager - Setup Required
echo ============================================
echo.
echo Python is required but not found in PATH.
echo.
echo Choose an option:
echo.
echo 1. I have Python installed (help me fix PATH)
echo 2. Install Python from Microsoft Store (easiest)
echo 3. Download Python from python.org
echo 4. Create temporary fix for this session
echo 5. Exit
echo.
choice /C 12345 /M "Select option"

if errorlevel 5 exit /b 0
if errorlevel 4 goto :temp_fix
if errorlevel 3 goto :download_python
if errorlevel 2 goto :store_python
if errorlevel 1 goto :fix_path

:fix_path
echo.
echo Searching for Python installations...
set FOUND_PATH=
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python39"
    "C:\Python311"
    "C:\Python310"
    "C:\Python39"
) do (
    if exist "%%~d\python.exe" (
        echo Found Python at: %%~d
        set "FOUND_PATH=%%~d"
        set "PYTHON_CMD=%%~d\python.exe"
        goto :create_launcher
    )
)
echo.
echo No Python installation found. Please install Python first.
pause
goto :python_not_found

:store_python
echo.
echo Opening Microsoft Store to install Python...
echo This will automatically configure everything.
echo.
echo After installation, run this launcher again.
start ms-windows-store://pdp/?productid=9NRWMJP3717K
pause
exit /b 0

:download_python
echo.
echo Opening Python download page...
echo.
echo IMPORTANT: During installation, make sure to:
echo  - Check "Add Python to PATH"
echo  - Click "Install Now"
echo.
echo After installation, run this launcher again.
start https://www.python.org/downloads/
pause
exit /b 0

:temp_fix
echo.
echo Creating temporary Python wrapper...
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python39"
    "C:\Python311"
    "C:\Python310"
    "C:\Python39"
) do (
    if exist "%%~d\python.exe" (
        set "PYTHON_CMD=%%~d\python.exe"
        set PYTHON_FOUND=1
        echo Found Python at: %%~d
        goto :found_python
    )
)
echo.
echo No Python installation found to create wrapper.
pause
goto :python_not_found

:create_launcher
echo.
echo Creating custom launcher with found Python...
(
    echo @echo off
    echo "!PYTHON_CMD!" pico_sync_manager.py
    echo if errorlevel 1 pause
) > PicoSync_Direct.bat
echo.
echo Created PicoSync_Direct.bat
echo You can use this to launch Pico Sync Manager.
echo.
choice /C YN /M "Launch Pico Sync Manager now"
if errorlevel 2 exit /b 0
set PYTHON_FOUND=1
goto :run_app

:found_python
REM Check if main script exists
if not exist "pico_sync_manager.py" (
    echo.
    echo ERROR: pico_sync_manager.py not found!
    echo Please ensure all files are in the same directory.
    echo.
    echo Current directory: %CD%
    echo.
    echo Files found:
    dir *.py 2>nul
    echo.
    pause
    exit /b 1
)

REM Quick dependency check
echo Checking dependencies...
!PYTHON_CMD! -c "import mpremote, serial, watchdog" >nul 2>&1
if !errorlevel! neq 0 (
    echo Installing required packages...
    echo This will only happen once...
    echo.
    !PYTHON_CMD! -m pip install mpremote pyserial watchdog
    echo.
)

:run_app
REM Clear screen and run
cls
echo ============================================
echo    Pico Sync Manager
echo ============================================
echo.
echo Starting application...
echo.

REM Run with pythonw if available (no console), otherwise python
set PYTHONW_CMD=!PYTHON_CMD:python.exe=pythonw.exe!
if exist "!PYTHONW_CMD!" (
    start "" "!PYTHONW_CMD!" pico_sync_manager.py
) else (
    start "" "!PYTHON_CMD!" pico_sync_manager.py
)

echo.
echo Pico Sync Manager launched!
echo.
echo This window will close in 5 seconds...
timeout /t 5 /nobreak >nul
exit /b 0