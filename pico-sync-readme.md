# Pico Sync Manager

A comprehensive GUI application for automated Raspberry Pi Pico development with real-time file synchronization.

## 🚀 Quick Start

### Option 1: Run with Python
```bash
# Install dependencies
pip install mpremote pyserial watchdog

# Run the application  
python pico_sync_manager.py
```

### Option 2: Create Standalone Executable
```bash
# Run the build script
python build_executable.py

# Then run the executable
./PicoSyncManager.exe  # Windows
./PicoSyncManager      # Linux/Mac
```

## 📋 Features

### Connection Management
- **Auto-Detection**: Automatically detects when a Pico is connected
- **Model Identification**: Identifies Pico (RP2040) vs Pico 2 (RP2350)
- **Visual Status**: LED indicator shows connection status
  - 🔴 Red = Disconnected
  - 🟢 Green = Connected

### File Synchronization
- **Auto Sync**: Monitors your project directory for changes
- **Real-time Updates**: Automatically uploads modified files
- **Selective Sync**: Choose which file types to sync
- **Queue Display**: Shows pending files during bulk operations

### Firmware Management
- **Auto Flash Check**: Detects if MicroPython is installed
- **Model-Specific Firmware**: Downloads correct firmware for your Pico
- **Guided Installation**: Step-by-step BOOTSEL mode instructions

### File Manager
- **Dual Pane View**: See local and Pico files side-by-side
- **Manual Operations**: Upload, delete, or manage individual files
- **File Details**: View size and modification times

## 🎮 How to Use

### Initial Setup

1. **Launch the Application**
   - Double-click `PicoSyncManager.exe` or run the Python script
   - The app will check and install dependencies automatically

2. **Select Your Project Directory**
   - Click "Browse" in the Controls panel
   - Choose the folder containing your Pico Python files

3. **Connect Your Pico**
   - Plug in your Pico via USB (normal mode, not BOOTSEL)
   - The LED should turn green when connected

### Automatic Synchronization

When "Auto Sync" is enabled:
- All `.py` files in your directory are synced on connection
- File changes are detected and uploaded automatically
- The sync queue shows pending operations

### Manual Operations

#### Flash Firmware
1. Click "Flash Firmware"
2. Select your Pico model (or use auto-detect)
3. Follow the BOOTSEL mode instructions
4. Firmware will be downloaded and flashed automatically

#### Sync Files Manually
- Click "Sync Now" to upload all files immediately
- Use the File Manager tab to upload individual files

#### Wipe Pico
- Click "Wipe Pico" to remove all files
- Useful for starting fresh or troubleshooting

## ⚙️ Settings

Access the Settings tab to configure:

- **File Types**: Which files to sync (default: `*.py`)
- **Subdirectories**: Include files in subdirectories
- **Auto Flash**: Automatically flash firmware on first connect
- **Notifications**: Desktop notifications for operations
- **Log Level**: Verbosity of logging (DEBUG/INFO/WARNING/ERROR)

## 🛠️ Troubleshooting

### Pico Not Detected
1. Ensure Pico is not in BOOTSEL mode
2. Check USB cable (must be data cable, not power-only)
3. Verify MicroPython is installed (use Flash Firmware)

### Sync Failures
1. Check the Logs tab for error details
2. Ensure correct firmware for your model:
   - Pico (RP2040): Use `RPI_PICO-xxx.uf2`
   - Pico 2 (RP2350): Use `RPI_PICO2-xxx.uf2`

### Common Issues

**"mpremote not found"**
- The app should install it automatically
- Manual install: `pip install mpremote`

**"No serial connection"**
- Wrong firmware for your Pico model
- Try reflashing with correct firmware

**Files not syncing**
- Check sync directory is set correctly
- Verify Auto Sync is enabled
- Check file types in Settings

## 📁 File Structure

```
PicoSyncManager/
├── pico_sync_manager.py    # Main application
├── build_executable.py     # Build script
├── run_pico_sync.bat      # Windows launcher
├── requirements.txt       # Python dependencies
└── PicoSyncManager.exe   # Standalone executable (after build)
```

## 🔧 Advanced Usage

### Command Line Arguments
```bash
# Run with specific config file
python pico_sync_manager.py --config /path/to/config.json

# Enable debug logging
python pico_sync_manager.py --debug
```

### Configuration File
Settings are saved to: `~/.pico_sync_config.json`

Example:
```json
{
  "sync_directory": "/path/to/project",
  "auto_sync": true,
  "file_types": "*.py",
  "sync_subdirs": true,
  "auto_flash": false,
  "show_notifications": true,
  "log_level": "INFO"
}
```

### Logs
Detailed logs are saved to: `~/.pico_sync_log.txt`

## 🎯 Tips & Best Practices

1. **Project Organization**
   - Keep all Pico files in one directory
   - Use subdirectories for modules
   - Name your main file `main.py` for auto-run

2. **Development Workflow**
   - Enable Auto Sync for rapid development
   - Use the log viewer to debug issues
   - Reset Pico after major changes

3. **Performance**
   - Disable subdirectory sync for large projects
   - Use manual sync for bulk updates
   - Monitor the sync queue for progress

## 🤝 Keyboard Shortcuts

- `Ctrl+O`: Open directory browser
- `Ctrl+S`: Manual sync
- `Ctrl+R`: Refresh file lists
- `Ctrl+L`: Clear log
- `F5`: Reset Pico

## 📞 Support

If you encounter issues:
1. Check the Logs tab for detailed error messages
2. Ensure you're using the correct firmware for your Pico model
3. Try the Wipe Pico option and resync
4. Verify all dependencies are installed

## 🔄 Updates

The application checks for:
- Dependency updates on startup
- Latest MicroPython firmware when flashing
- Configuration compatibility

---

Made for Raspberry Pi Pico developers who want a seamless development experience! 🚀