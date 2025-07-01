@echo off
REM ────────────────────────────────────────────────────────────────
REM 1) Elevation: restart as Admin if needed
net session >nul 2>&1 || (
  echo ⚠️ Relaunching as administrator…
  powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)

REM 2) Define source & install target
set "SRC=%~dp0"
set "DST=%ProgramFiles%\PicoSync"

REM 3) Make sure install folder exists
if not exist "%DST%" mkdir "%DST%"

REM 4) Copy EVERYTHING (including app.ico)
xcopy "%SRC%*" "%DST%\" /E /I /Y >nul

REM 5) Confirm icon got copied
set "ICON=%DST%\backend\config\core\app.ico"
if not exist "%ICON%" (
  echo ❌ Icon not found at "%ICON%"
  pause
  exit /b
)

REM 6) Create desktop shortcut with icon index “,0”
set "LNK=%USERPROFILE%\Desktop\PicoSync.lnk"
powershell -NoProfile -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LNK%');" ^
  "$s.TargetPath='%DST%\run.bat';" ^
  "$s.WorkingDirectory='%DST%';" ^
  "$s.IconLocation='%ICON%,0';" ^
  "$s.Save();"

echo.
echo ✅ Installed to: %DST%
echo ✅ Shortcut: %LNK%  (icon: %ICON%,0)
pause
