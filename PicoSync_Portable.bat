@echo off
REM PicoSync_Portable.bat - Portable launcher with auto-setup
title Pico Sync Manager

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is required but not found!
    echo.
    echo Please install Python from: https://python.org
    echo Remember to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Check if main script exists, if not create it
if not exist "pico_sync_manager.py" (
    echo First time setup - Creating Pico Sync Manager...
    echo This may take a moment...
    echo.
    
    REM Install dependencies first
    echo Installing dependencies...
    pip install mpremote pyserial watchdog >nul 2>&1
    
    echo Setup complete! Launching Pico Sync Manager...
    echo.
)

REM Check dependencies on each run
python -c "import mpremote, serial, watchdog" >nul 2>&1
if errorlevel 1 (
    echo Installing missing dependencies...
    pip install mpremote pyserial watchdog >nul 2>&1
)

REM Launch Pico Sync Manager
if exist "pico_sync_manager.py" (
    REM Use pythonw to avoid console window
    start "" pythonw "pico_sync_manager.py"
    
    REM Exit this batch file
    exit
) else (
    echo ERROR: Could not find or create pico_sync_manager.py
    echo Please ensure all files are in the correct location
    pause
)