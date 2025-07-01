@echo off
cd /d "%~dp0"
if not exist "pico_venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run pico_installer.py first
    pause
    exit /b 1
)
"pico_venv\Scripts\python.exe" "pico_sync_manager.py" %*
if errorlevel 1 pause
