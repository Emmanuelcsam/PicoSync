# PicoSync - Raspberry Pi Pico Development Manager

A cross-platform GUI application for managing Raspberry Pi Pico development with automatic file synchronization, firmware flashing, and file management.

## Features

- Auto-detection of connected Raspberry Pi Pico devices
- Real-time file synchronization with watch mode
- Firmware flashing support for both RP2040 and RP2350
- Dual-pane file manager (local and remote)
- Cross-platform support (Windows and Linux)

## Quick Start

### Windows
Double-click `PicoSync_Windows.bat` to install and run PicoSync.

### Linux
Run the following command in terminal:
```bash
./PicoSync_Linux.sh
```

## Requirements

- Python 3.6 or higher
- pip (Python package manager)
- USB access permissions (Linux users may need to be in 'dialout' group)

## File Structure

- `pico_sync_manager.py` - Main application
- `pico_installer.py` - Universal installer script
- `requirements.txt` - Python dependencies
- `PicoSync_Windows.bat` - Windows launcher
- `PicoSync_Linux.sh` - Linux launcher

## Manual Installation

If the automatic installers don't work, you can install manually:

1. Install Python 3.6+ from https://www.python.org/
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python pico_sync_manager.py`

## Troubleshooting

### Linux USB Permissions
If you get permission errors accessing the Pico:
```bash
sudo usermod -a -G dialout $USER
```
Then log out and back in.

### Windows Python Not Found
Make sure Python is added to your PATH during installation, or reinstall Python and check "Add Python to PATH".

## Legacy Files

All previous files have been moved to the `old/` directory for reference.