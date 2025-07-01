@echo off
REM Universal run shortcut for PicoSync
REM References icon from backend\config\core\run.ico

REM Get the directory of this script
set SCRIPT_DIR=%~dp0

REM Run the application from backend
cd /d "%SCRIPT_DIR%backend"
call run_picosync.bat