@echo off
REM fix_python_path.bat - Quick fix for Python PATH issues
title Fix Python PATH

echo ============================================
echo    Python PATH Quick Fix
echo ============================================
echo.
echo This script will help you fix Python PATH issues.
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as Administrator
    echo Some fixes may require admin rights
    echo.
)

echo Searching for Python installations...
echo.

set FOUND_PYTHON=0
set PYTHON_PATHS=

REM Search common locations
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python39"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python312"
    "C:\Python39"
    "C:\Python310" 
    "C:\Python311"
    "C:\Python312"
    "%PROGRAMFILES%\Python39"
    "%PROGRAMFILES%\Python310"
    "%PROGRAMFILES%\Python311"
    "%PROGRAMFILES(x86)%\Python39"
    "%PROGRAMFILES(x86)%\Python310"
) do (
    if exist "%%~d\python.exe" (
        echo [FOUND] Python at: %%~d
        set FOUND_PYTHON=1
        set "PYTHON_PATHS=!PYTHON_PATHS!;%%~d;%%~d\Scripts"
    )
)

REM Check Microsoft Store Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('where python') do (
        echo [FOUND] Python at: %%i
        set FOUND_PYTHON=1
    )
)

echo.

if %FOUND_PYTHON% equ 0 (
    echo [ERROR] No Python installations found!
    echo.
    echo Please install Python first:
    echo 1. Download from: https://www.python.org/downloads/
    echo 2. Or install from Microsoft Store
    echo.
    echo Opening Python download page...
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ============================================
echo    Quick Fixes Available:
echo ============================================
echo.
echo 1. Add Python to PATH for current session only
echo 2. Create python.bat wrapper (works immediately)
echo 3. Show manual PATH instructions
echo 4. Install from Microsoft Store (recommended)
echo 5. Exit
echo.
choice /C 12345 /M "Select an option"

if errorlevel 5 goto :end
if errorlevel 4 goto :install_store
if errorlevel 3 goto :show_manual
if errorlevel 2 goto :create_wrapper
if errorlevel 1 goto :temp_path

:temp_path
echo.
echo Adding Python to PATH for this session...
set "PATH=%PATH%%PYTHON_PATHS%"
echo.
echo [OK] Python added to PATH for this session
echo.
echo Testing Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python still not working
) else (
    echo [OK] Python is working!
    echo.
    echo NOTE: This is temporary. To make permanent, use option 3.
)
echo.
pause
goto :menu

:create_wrapper
echo.
echo Creating python.bat wrapper...
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python39"
    "C:\Python311"
    "C:\Python310"
    "C:\Python39"
) do (
    if exist "%%~d\python.exe" (
        echo @echo off > python.bat
        echo "%%~d\python.exe" %%* >> python.bat
        
        echo @echo off > pip.bat
        echo "%%~d\python.exe" -m pip %%* >> pip.bat
        
        echo [OK] Created python.bat and pip.bat wrappers
        echo.
        echo You can now use 'python' and 'pip' commands!
        echo These files must stay in the current directory.
        goto :wrapper_done
    )
)
:wrapper_done
echo.
pause
goto :menu

:show_manual
echo.
echo ============================================
echo    Manual PATH Configuration
echo ============================================
echo.
echo 1. Press Win+X and select "System"
echo 2. Click "Advanced system settings"
echo 3. Click "Environment Variables"
echo 4. Under "System variables", find "Path"
echo 5. Click "Edit"
echo 6. Click "New" and add these paths:
echo.
for %%d in (
    "%LOCALAPPDATA%\Programs\Python\Python311"
    "%LOCALAPPDATA%\Programs\Python\Python310"
    "%LOCALAPPDATA%\Programs\Python\Python39"
    "C:\Python311"
    "C:\Python310"
    "C:\Python39"
) do (
    if exist "%%~d\python.exe" (
        echo    %%~d
        echo    %%~d\Scripts
        echo.
    )
)
echo 7. Click OK on all windows
echo 8. Restart Command Prompt
echo.
pause
goto :menu

:install_store
echo.
echo Opening Microsoft Store to install Python...
echo.
echo This is the easiest method and automatically configures PATH.
echo.
start ms-windows-store://pdp/?productid=9NRWMJP3717K
echo After installation, restart this script.
echo.
pause
goto :end

:menu
echo.
echo Return to main menu? (Y/N)
choice /C YN
if errorlevel 2 goto :end
if errorlevel 1 goto :start

:end
echo.
echo Exiting...
exit /b 0