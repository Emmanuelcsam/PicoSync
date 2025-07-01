@echo off
setlocal enabledelayedexpansion

:: PicoSync Windows Launcher
:: Auto-detects Python and runs the installer/application

title PicoSync

:: Check if already installed (launcher exists)
if exist "PicoSync.bat" (
    echo PicoSync is already installed. Launching...
    call PicoSync.bat
    goto :end
)

:: Try to find Python
echo Detecting Python installation...

:: Method 1: Try python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    goto :found_python
)

:: Method 2: Try python3 command
python3 --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python3
    goto :found_python
)

:: Method 3: Try py launcher
py --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=py
    goto :found_python
)

:: Method 4: Check common installation paths
for %%i in (
    "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"
    "C:\Python3*\python.exe"
    "C:\Python*\python.exe"
    "%ProgramFiles%\Python3*\python.exe"
    "%ProgramFiles%\Python*\python.exe"
    "%ProgramFiles(x86)%\Python3*\python.exe"
    "%ProgramFiles(x86)%\Python*\python.exe"
) do (
    if exist "%%~i" (
        set "PYTHON_CMD=%%~i"
        goto :found_python
    )
)

:: Python not found
echo.
echo ERROR: Python not found!
echo.
echo Please install Python 3.6 or higher from:
echo https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation!
echo.
pause
exit /b 1

:found_python
echo Found Python: %PYTHON_CMD%
echo.

:: Run the installer
echo Running PicoSync installer...
"%PYTHON_CMD%" pico_installer.py

if !errorlevel! equ 0 (
    echo.
    echo Installation complete! You can now run PicoSync.bat
    echo.
    :: Try to launch the app
    if exist "PicoSync.bat" (
        echo Launching PicoSync...
        timeout /t 2 /nobreak >nul
        call PicoSync.bat
    )
) else (
    echo.
    echo Installation failed. Please check the error messages above.
    pause
)

:end
endlocal