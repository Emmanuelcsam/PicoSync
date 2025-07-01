@echo off
REM Universal installation shortcut for PicoSync
REM References icon from backend\config\core\install.ico

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Run the installation script from backend
cd /d "%SCRIPT_DIR%backend"
call install_picosync.bat