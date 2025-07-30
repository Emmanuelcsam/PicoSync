# PicoSync - Optimized Setup Guide

## Quick Start

### Windows
1. **First Run (Installation)**: Double-click `install_picosync.bat`
2. **Subsequent Runs**: Double-click `run_picosync.bat`

### Linux
1. **First Run (Installation)**: Run `./install_picosync.sh`
2. **Subsequent Runs**: Run `./run_picosync.sh`

## What This Does

The installer will:
- Install UV package manager (if not present)
- Create a Python virtual environment
- Install all required dependencies
- Create desktop shortcuts/menu entries
- Save configuration for future runs

## File Structure

```
pico/
├── install_picosync.py     # Universal installer (Python)
├── install_picosync.bat    # Windows installer shortcut
├── install_picosync.sh     # Linux installer shortcut
├── run_picosync.py         # Universal runner (Python)
├── run_picosync.bat        # Windows run shortcut
├── run_picosync.sh         # Linux run shortcut
├── config/                 # Organized configuration
│   ├── core/              # Main application files
│   │   ├── pico_sync_manager.py
│   │   ├── requirements.txt
│   │   └── icon.ico
│   ├── firmware/          # Pico firmware files
│   ├── scripts/           # Helper scripts
│   └── docs/              # Documentation
└── pico_venv/             # Virtual environment (created by installer)
```

## Transferring to Another Computer

1. Copy the entire `pico` folder
2. Run the installer on the new computer
3. That's it! All paths are relative

## Troubleshooting

### Python Not Found
- Windows: Install from https://www.python.org (check "Add to PATH")
- Linux: `sudo apt install python3 python3-pip python3-venv`

### UV Installation Failed
- Manual install: https://docs.astral.sh/uv/

### USB Permissions (Linux)
```bash
sudo usermod -a -G dialout $USER
# Then log out and back in
```

## Manual Installation (if scripts fail)

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv pico_venv

# Install dependencies
uv pip install -r config/core/requirements.txt

# Run the application
uv run python config/core/pico_sync_manager.py
```