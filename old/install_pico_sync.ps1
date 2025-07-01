# install_pico_sync.ps1 - PowerShell installer for Pico Sync Manager
# Run this with: powershell -ExecutionPolicy Bypass -File install_pico_sync.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Pico Sync Manager - PowerShell Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Function to test Python command
function Test-PythonCommand {
    param($cmd)
    try {
        $output = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Find Python
$pythonCmd = $null
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    if (Test-PythonCommand $cmd) {
        $pythonCmd = $cmd
        Write-Host "[OK] Found Python as '$cmd'" -ForegroundColor Green
        & $cmd --version
        break
    }
}

# Check common Python locations if not found in PATH
if (-not $pythonCmd) {
    $pythonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe"
    )
    
    foreach ($path in $pythonPaths) {
        if (Test-Path $path) {
            $pythonCmd = $path
            Write-Host "[OK] Found Python at: $path" -ForegroundColor Green
            break
        }
    }
}

# If Python not found, offer to install it
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python is not installed or not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Would you like to install Python automatically? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Downloading Python installer..." -ForegroundColor Cyan
        $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
        $installerPath = "$env:TEMP\python-installer.exe"
        
        try {
            Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
            Write-Host "Installing Python (this may take a few minutes)..." -ForegroundColor Cyan
            Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1" -Wait
            
            # Refresh environment
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            # Try to find Python again
            foreach ($cmd in $pythonCommands) {
                if (Test-PythonCommand $cmd) {
                    $pythonCmd = $cmd
                    Write-Host "[OK] Python installed successfully!" -ForegroundColor Green
                    break
                }
            }
        } catch {
            Write-Host "[ERROR] Failed to install Python: $_" -ForegroundColor Red
        }
    }
    
    if (-not $pythonCmd) {
        Write-Host ""
        Write-Host "Please install Python manually from: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "Remember to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to open the Python download page..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        Start-Process "https://www.python.org/downloads/"
        exit 1
    }
}

Write-Host ""

# Check if main script exists
if (-not (Test-Path "pico_sync_manager.py")) {
    Write-Host "[ERROR] pico_sync_manager.py not found!" -ForegroundColor Red
    Write-Host "Please ensure all files are in the current directory" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install required packages
Write-Host "Installing required packages..." -ForegroundColor Cyan
Write-Host "This may take a minute..." -ForegroundColor Gray
Write-Host ""

$packages = @("mpremote", "pyserial", "watchdog")

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Gray
    & $pythonCmd -m pip install $package --quiet
}

# Verify installation
Write-Host ""
Write-Host "Verifying installation..." -ForegroundColor Cyan
$verifyScript = @"
try:
    import mpremote, serial, watchdog
    print('[OK] All packages installed successfully')
except ImportError as e:
    print(f'[ERROR] Missing package: {e}')
    exit(1)
"@

$verifyResult = & $pythonCmd -c $verifyScript 2>&1
Write-Host $verifyResult -ForegroundColor $(if ($LASTEXITCODE -eq 0) { "Green" } else { "Red" })

# Create custom launcher
Write-Host ""
Write-Host "Creating launcher script..." -ForegroundColor Cyan

$launcherContent = @"
@echo off
title Pico Sync Manager
echo Starting Pico Sync Manager...
"$pythonCmd" "%~dp0pico_sync_manager.py" %*
if errorlevel 1 pause
"@

$launcherContent | Out-File -FilePath "PicoSyncManager.bat" -Encoding ASCII
Write-Host "[OK] Created PicoSyncManager.bat" -ForegroundColor Green

# Create desktop shortcut
Write-Host ""
Write-Host "Creating desktop shortcut..." -ForegroundColor Cyan

$WshShell = New-Object -comObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$Shortcut = $WshShell.CreateShortcut("$Desktop\Pico Sync Manager.lnk")
$Shortcut.TargetPath = "$PWD\PicoSyncManager.bat"
$Shortcut.WorkingDirectory = $PWD
$Shortcut.WindowStyle = 7  # Minimized
$Shortcut.Description = "Pico Sync Manager - Automated Pico Development Tool"
$Shortcut.Save()

if (Test-Path "$Desktop\Pico Sync Manager.lnk") {
    Write-Host "[OK] Desktop shortcut created" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Could not create desktop shortcut" -ForegroundColor Yellow
}

# Create Start Menu entry
$StartMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Pico Sync Manager"
if (-not (Test-Path $StartMenu)) {
    New-Item -ItemType Directory -Path $StartMenu -Force | Out-Null
}

$StartShortcut = $WshShell.CreateShortcut("$StartMenu\Pico Sync Manager.lnk")
$StartShortcut.TargetPath = "$PWD\PicoSyncManager.bat"
$StartShortcut.WorkingDirectory = $PWD
$StartShortcut.WindowStyle = 7
$StartShortcut.Description = "Pico Sync Manager"
$StartShortcut.Save()

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    Installation Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pico Sync Manager has been installed with:" -ForegroundColor Green
Write-Host "  - Desktop shortcut" -ForegroundColor Gray
Write-Host "  - Start Menu entry" -ForegroundColor Gray
Write-Host "  - Custom launcher (PicoSyncManager.bat)" -ForegroundColor Gray
Write-Host "  - All required dependencies" -ForegroundColor Gray
Write-Host ""
Write-Host "You can now run Pico Sync Manager by:" -ForegroundColor Cyan
Write-Host "  1. Double-clicking the desktop shortcut" -ForegroundColor Gray
Write-Host "  2. Running: PicoSyncManager.bat" -ForegroundColor Gray
Write-Host "  3. Running: $pythonCmd pico_sync_manager.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Would you like to start Pico Sync Manager now? (Y/N)" -ForegroundColor Yellow
$startNow = Read-Host

if ($startNow -eq 'Y' -or $startNow -eq 'y') {
    Write-Host ""
    Write-Host "Starting Pico Sync Manager..." -ForegroundColor Cyan
    Start-Process -FilePath "PicoSyncManager.bat"
} else {
    Write-Host ""
    Write-Host "You can start Pico Sync Manager anytime using the desktop shortcut." -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")