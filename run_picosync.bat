@echo off
setlocal enabledelayedexpansion

:: PicoSync Windows Runner
:: Runs PicoSync with proper environment

title PicoSync

:: Set icon for this batch file
powershell -Command "& {$shell = New-Object -ComObject Shell.Application; $folder = $shell.Namespace('%~dp0backend\config\core'); $file = $folder.ParseName('run.ico'); $shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut('%~f0.lnk'); $shortcut.IconLocation = $file.Path; $shortcut.Save(); Remove-Item '%~f0.lnk' -Force}" >nul 2>&1

:: Create shortcut with embedded icon for better File Explorer display
powershell -Command "& {$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%~dp0PicoSync_Run.lnk'); $Shortcut.TargetPath = '%~f0'; $Shortcut.IconLocation = '%~dp0backend\config\core\run.ico'; $Shortcut.Save()}" >nul 2>&1

:: Check if config exists
if not exist "backend\picosync_config.json" (
    echo ERROR: PicoSync is not installed!
    echo.
    echo Please run the installer first:
    echo   install_picosync.bat
    echo.
    pause
    exit /b 1
)

:: Try to find Python (same methods as installer)
:: Try python command
python --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python
    goto :run_app
)

:: Try python3 command
python3 --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=python3
    goto :run_app
)

:: Try py launcher
py --version >nul 2>&1
if !errorlevel! equ 0 (
    set PYTHON_CMD=py
    goto :run_app
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
        goto :run_app
    )
)

:: Python not found
echo ERROR: Python not found!
echo Please ensure Python is installed and in PATH
pause
exit /b 1

:run_app
:: Run the application
"%PYTHON_CMD%" "%~dp0backend\run_picosync.py"

:: Pause only on error
if !errorlevel! neq 0 (
    echo.
    echo PicoSync exited with an error.
    pause
)

endlocal