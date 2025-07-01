@echo off
setlocal enabledelayedexpansion

:: PicoSync Windows Installer
:: Automatically detects Python and runs the installer

title PicoSync Installer

echo =====================================
echo    PicoSync Windows Installer
echo =====================================
echo.

:: Check for Python
echo Checking for Python installation...

:: Try python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    goto :run_installer
)

:: Try python3 command
python3 --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python3
    goto :run_installer
)

:: Try py launcher
py --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=py
    goto :run_installer
)

:: Check common paths
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python3*\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python*\python.exe"
    "C:\Python3*\python.exe"
    "C:\Python*\python.exe"
) do (
    if exist "%%~p" (
        set "PYTHON_CMD=%%~p"
        goto :run_installer
    )
)

:: Python not found
echo.
echo ERROR: Python not found!
echo.
echo Please install Python 3.8 or higher from:
echo https://www.python.org/downloads/
echo.
echo IMPORTANT: Check "Add Python to PATH" during installation!
echo.
pause
exit /b 1

:run_installer
echo Found Python: %PYTHON_CMD%
echo.
echo Starting installation...
echo.

:: Run the installer
"%PYTHON_CMD%" "%~dp0install_picosync.py"

if !errorlevel! equ 0 (
    echo.
    echo =====================================
    echo    Installation Complete!
    echo =====================================
    echo.
    echo You can now run PicoSync by:
    echo   - Double-clicking run_picosync.bat
    echo   - Using the Start Menu shortcut
    echo.
) else (
    echo.
    echo Installation failed!
    echo Please check the error messages above.
)

pause
endlocal