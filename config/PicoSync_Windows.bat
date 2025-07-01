@echo off
setlocal enabledelayedexpansion

:: PicoSync Windows Universal Launcher
:: Auto-detects Python, installs if needed, and runs the application

title PicoSync Launcher

:: Check if virtual environment exists and is valid
if exist "pico_venv\Scripts\python.exe" (
    echo Virtual environment found. Launching PicoSync...
    "pico_venv\Scripts\python.exe" "pico_sync_manager.py" %*
    if errorlevel 1 pause
    goto :end
)

:: Check if PicoSync.bat exists but is incorrect
if exist "PicoSync.bat" (
    :: Check if it's using the virtual environment
    findstr /C:"pico_venv" "PicoSync.bat" >nul
    if errorlevel 1 (
        echo Found outdated PicoSync.bat. Recreating...
        del PicoSync.bat
    )
)

:: Try to find Python
echo Detecting Python installation...

set PYTHON_CMD=
set PYTHON_FOUND=0

:: Method 1: Try python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    set PYTHON_CMD=python
    set PYTHON_FOUND=1
    goto :check_version
)

:: Method 2: Try python3 command
python3 --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VER=%%i
    set PYTHON_CMD=python3
    set PYTHON_FOUND=1
    goto :check_version
)

:: Method 3: Try py launcher
py --version >nul 2>&1
if !errorlevel! equ 0 (
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PYTHON_VER=%%i
    set PYTHON_CMD=py -3
    set PYTHON_FOUND=1
    goto :check_version
)

:: Method 4: Check registry for Python installations
echo Checking registry for Python installations...

:: Check HKLM and HKCU for Python installations
for %%R in (HKLM HKCU) do (
    for /f "tokens=*" %%i in ('reg query "%%R\SOFTWARE\Python\PythonCore" 2^>nul ^| findstr /i "PythonCore"') do (
        for /f "tokens=3" %%j in ('reg query "%%i\InstallPath" /ve 2^>nul ^| findstr REG_SZ') do (
            if exist "%%j\python.exe" (
                set "PYTHON_CMD=%%j\python.exe"
                set PYTHON_FOUND=1
                goto :check_version
            )
        )
    )
)

:: Method 5: Check common installation paths
for %%i in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python37\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python36\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "C:\Python38\python.exe"
    "C:\Python37\python.exe"
    "C:\Python36\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles%\Python39\python.exe"
    "%ProgramFiles%\Python38\python.exe"
    "%ProgramFiles(x86)%\Python313\python.exe"
    "%ProgramFiles(x86)%\Python312\python.exe"
    "%ProgramFiles(x86)%\Python311\python.exe"
) do (
    if exist "%%~i" (
        set "PYTHON_CMD=%%~i"
        set PYTHON_FOUND=1
        goto :check_version
    )
)

:check_version
if !PYTHON_FOUND! equ 1 (
    echo Found Python: !PYTHON_CMD!
    
    :: Check Python version is 3.6 or higher
    "!PYTHON_CMD!" -c "import sys; exit(0 if sys.version_info >= (3, 6) else 1)" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python 3.6 or higher is required!
        set PYTHON_FOUND=0
    )
)

if !PYTHON_FOUND! equ 0 (
    echo.
    echo ERROR: Python 3.6+ not found!
    echo.
    echo Would you like to download Python now?
    echo.
    choice /C YN /N /M "Download Python? (Y/N): "
    if errorlevel 2 goto :python_manual
    if errorlevel 1 goto :download_python
)

:: Found valid Python, continue with installation
goto :run_installer

:download_python
echo.
echo Opening Python download page...
start https://www.python.org/downloads/
echo.
echo Please download and install Python 3.6 or higher.
echo IMPORTANT: Check "Add Python to PATH" during installation!
echo.
echo After installing Python, run this script again.
pause
goto :end

:python_manual
echo.
echo Please install Python 3.6 or higher from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: Check "Add Python to PATH" during installation!
echo.
pause
goto :end

:run_installer
:: Check if installer exists
if not exist "pico_installer.py" (
    echo ERROR: pico_installer.py not found!
    echo Please make sure all PicoSync files are in the current directory.
    pause
    goto :end
)

:: Run the installer
echo.
echo Running PicoSync installer...
echo This will set up a virtual environment and install dependencies...
echo.

"!PYTHON_CMD!" pico_installer.py

if !errorlevel! equ 0 (
    echo.
    echo =========================================
    echo Installation successful!
    echo =========================================
    echo.
    
    :: Create proper PicoSync.bat if it doesn't exist
    if not exist "PicoSync.bat" (
        echo Creating PicoSync.bat launcher...
        (
            echo @echo off
            echo cd /d "%%~dp0"
            echo.
            echo :: Check if virtual environment exists
            echo if not exist "pico_venv\Scripts\python.exe" ^(
            echo     echo ERROR: Virtual environment not found!
            echo     echo Please run pico_installer.py first
            echo     echo.
            echo     pause
            echo     exit /b 1
            echo ^)
            echo.
            echo :: Run PicoSync using the virtual environment
            echo "pico_venv\Scripts\python.exe" "pico_sync_manager.py" %%*
            echo if errorlevel 1 pause
        ) > PicoSync.bat
    )
    
    :: Launch PicoSync
    if exist "pico_venv\Scripts\python.exe" (
        echo.
        echo Launching PicoSync...
        echo.
        timeout /t 2 /nobreak >nul
        "pico_venv\Scripts\python.exe" "pico_sync_manager.py" %*
        if errorlevel 1 pause
    ) else (
        echo ERROR: Virtual environment not created properly!
        pause
    )
) else (
    echo.
    echo =========================================
    echo Installation failed!
    echo =========================================
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo - Internet connection required for downloading packages
    echo - Antivirus may block pip installations
    echo - Try running as Administrator if permission errors occur
    echo.
    pause
)

:end
endlocal