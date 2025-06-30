@echo off
REM run_pico_sync.bat - Launch Pico Sync Manager
title Pico Sync Manager

echo Starting Pico Sync Manager...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if the script exists
if not exist "pico_sync_manager.py" (
    echo pico_sync_manager.py not found!
    echo Please ensure the Python script is in the same directory as this batch file
    pause
    exit /b 1
)

REM Run the Pico Sync Manager
python pico_sync_manager.py

REM If the script exits, pause to see any error messages
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)