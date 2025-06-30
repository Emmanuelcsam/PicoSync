@echo off
REM START_HERE.bat - The ultimate launcher that handles everything
color 0A
title Pico Sync Manager - Getting Started

:main_menu
cls
echo.
echo    ____  _            ____                      __  __                                   
echo   / __ \(_)________  / ___/__  ______  _____   /  \/  /___ _____  ____ _____ ____  _____
echo  / /_/ / / ___/ __ \ \__ \/ / / / __ \/ ___/  / /\_/ / __ `/ __ \/ __ `/ __ `/ _ \/ ___/
echo / ____/ / /__/ /_/ /___/ / /_/ / / / / /__   / /  / / /_/ / / / / /_/ / /_/ /  __/ /    
echo /_/   /_/\___/\____//____/\__, /_/ /_/\___/  /_/  /_/\__,_/_/ /_/\__,_/\__, /\___/_/     
echo                          /____/                                        /____/             
echo.
echo ================================================================================
echo                          Welcome to Pico Sync Manager!
echo ================================================================================
echo.

REM Quick Python check
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [✓] Python detected! Ready to go.
    echo.
    echo Press any key to start Pico Sync Manager...
    pause >nul
    goto :run_with_python
)

python3 --version >nul 2>&1
if %errorlevel% == 0 (
    echo [✓] Python3 detected! Ready to go.
    echo.
    echo Press any key to start Pico Sync Manager...
    pause >nul
    goto :run_with_python3
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    echo [✓] Python detected via py launcher! Ready to go.
    echo.
    echo Press any key to start Pico Sync Manager...
    pause >nul
    goto :run_with_py
)

REM Python not in PATH - show options
echo [!] Python is not detected in your PATH.
echo.
echo Don't worry! I'll help you get started. Choose an option:
echo.
echo   1. 🔍 Search for Python on this computer
echo   2. 🏪 Install Python from Microsoft Store (Easiest!)
echo   3. 🌐 Download Python from python.org
echo   4. 📋 I know Python is installed (show me how to fix it)
echo   5. ❌ Exit
echo.
choice /C 12345 /N /M "Select an option (1-5): "

if errorlevel 5 exit /b 0
if errorlevel 4 goto :fix_instructions
if errorlevel 3 goto :download_web
if errorlevel 2 goto :install_store
if errorlevel 1 goto :search_python

:search_python
cls
echo.
echo ================================================================================
echo                         Searching for Python...
echo ================================================================================
echo.

set FOUND=0
set PY_PATH=

for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Python39\python.exe"
    "C:\Python38\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles%\Python39\python.exe"
    "%ProgramFiles(x86)%\Python312\python.exe"
    "%ProgramFiles(x86)%\Python311\python.exe"
    "%ProgramFiles(x86)%\Python310\python.exe"
    "%ProgramFiles(x86)%\Python39\python.exe"
) do (
    if exist %%p (
        echo [✓] Found Python at: %%p
        set FOUND=1
        set "PY_PATH=%%p"
        goto :found_local_python
    )
)

if %FOUND% == 0 (
    echo.
    echo [✗] No Python installation found.
    echo.
    echo You'll need to install Python first.
    echo.
    pause
    goto :main_menu
)

:found_local_python
echo.
echo Great! I found Python on your computer.
echo.
echo What would you like to do?
echo.
echo   1. 🚀 Create a shortcut to run Pico Sync Manager
echo   2. 🔧 Add Python to PATH permanently (requires restart)
echo   3. 📝 Show me manual instructions
echo   4. ← Back to main menu
echo.
choice /C 1234 /N /M "Select an option (1-4): "

if errorlevel 4 goto :main_menu
if errorlevel 3 goto :fix_instructions
if errorlevel 2 goto :add_to_path
if errorlevel 1 goto :create_shortcut

:create_shortcut
echo.
echo Creating shortcuts...
echo.

REM Create direct launcher
(
    echo @echo off
    echo title Pico Sync Manager
    echo "%PY_PATH%" "%~dp0pico_sync_manager.py"
    echo if errorlevel 1 pause
) > "Pico_Sync_Manager.bat"

REM Create desktop shortcut
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%USERPROFILE%\Desktop\Pico Sync Manager.lnk'); $SC.TargetPath = '%CD%\Pico_Sync_Manager.bat'; $SC.WorkingDirectory = '%CD%'; $SC.Description = 'Pico Sync Manager'; $SC.Save()"

echo.
echo [✓] Created Pico_Sync_Manager.bat
echo [✓] Created Desktop shortcut
echo.
echo You can now:
echo   - Double-click "Pico_Sync_Manager.bat" in this folder
echo   - Use the desktop shortcut
echo.
choice /C YN /N /M "Start Pico Sync Manager now? (Y/N): "
if errorlevel 2 goto :done
if errorlevel 1 (
    start "" "Pico_Sync_Manager.bat"
    goto :done
)

:add_to_path
echo.
echo To add Python to PATH permanently:
echo.
echo 1. I'll open the Environment Variables window
echo 2. Click "Edit" on the Path variable
echo 3. Add these two entries:
echo    - %PY_PATH:~0,-11%
echo    - %PY_PATH:~0,-11%Scripts
echo 4. Click OK and restart your computer
echo.
echo Press any key to open Environment Variables...
pause >nul
rundll32.exe sysdm.cpl,EditEnvironmentVariables
goto :done

:install_store
cls
echo.
echo ================================================================================
echo                    Installing Python from Microsoft Store
echo ================================================================================
echo.
echo This is the EASIEST method! Here's what will happen:
echo.
echo 1. Microsoft Store will open
echo 2. Search for "Python 3.11" (recommended)
echo 3. Click "Get" or "Install"
echo 4. Wait for installation (about 1 minute)
echo 5. Run this script again - it will work!
echo.
echo Benefits:
echo   ✓ Automatically adds Python to PATH
echo   ✓ Easy updates through Store
echo   ✓ No configuration needed
echo.
echo Press any key to open Microsoft Store...
pause >nul
start ms-windows-store://search/?query=python
echo.
echo After installation is complete, run START_HERE.bat again.
echo.
pause
exit /b 0

:download_web
cls
echo.
echo ================================================================================
echo                    Downloading Python from Python.org
echo ================================================================================
echo.
echo I'll open the Python download page. Here's what to do:
echo.
echo 1. Click the big yellow "Download Python" button
echo 2. Run the downloaded installer
echo.
echo ⚠️  IMPORTANT - On the first installer screen:
echo    ✓ CHECK the box that says "Add Python to PATH"
echo    (It's at the bottom of the window)
echo.
echo 3. Click "Install Now"
echo 4. Wait for installation
echo 5. Run this script again
echo.
echo Press any key to open the download page...
pause >nul
start https://www.python.org/downloads/
echo.
echo After installation is complete, run START_HERE.bat again.
echo.
pause
exit /b 0

:fix_instructions
cls
echo.
echo ================================================================================
echo                         Python PATH Fix Instructions
echo ================================================================================
echo.
echo If Python is installed but not working, here's how to fix it:
echo.
echo STEP 1: Find where Python is installed
echo   Common locations:
echo   - C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\
echo   - C:\Python311\
echo   - C:\Program Files\Python311\
echo.
echo STEP 2: Add to PATH
echo   1. Press Windows + X
echo   2. Click "System"
echo   3. Click "Advanced system settings"
echo   4. Click "Environment Variables"
echo   5. Under "System variables", find "Path"
echo   6. Click "Edit"
echo   7. Click "New" and add:
echo      - The Python folder (e.g., C:\Python311\)
echo      - The Scripts folder (e.g., C:\Python311\Scripts\)
echo   8. Click OK on all windows
echo   9. Restart Command Prompt
echo.
echo Press any key to return to menu...
pause >nul
goto :main_menu

:run_with_python
if not exist "pico_sync_manager.py" goto :missing_files
echo Starting Pico Sync Manager...
python pico_sync_manager.py
if errorlevel 1 pause
exit /b 0

:run_with_python3
if not exist "pico_sync_manager.py" goto :missing_files
echo Starting Pico Sync Manager...
python3 pico_sync_manager.py
if errorlevel 1 pause
exit /b 0

:run_with_py
if not exist "pico_sync_manager.py" goto :missing_files
echo Starting Pico Sync Manager...
py pico_sync_manager.py
if errorlevel 1 pause
exit /b 0

:missing_files
echo.
echo ERROR: pico_sync_manager.py not found!
echo.
echo Make sure all files are in the same folder:
echo   - START_HERE.bat (this file)
echo   - pico_sync_manager.py
echo.
echo Current folder: %CD%
echo.
pause
exit /b 1

:done
echo.
echo ================================================================================
echo                                    All Done!
echo ================================================================================
echo.
echo Pico Sync Manager is ready to use!
echo.
echo For help and documentation, check the README.md file.
echo.
pause
exit /b 0