#!/bin/bash

# PicoSync Linux Installer
# Automatically detects Python and runs the installer

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================="
echo -e "    PicoSync Linux Installer"
echo -e "=====================================${NC}"
echo

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    if command -v "$python_cmd" &> /dev/null; then
        local version=$("$python_cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if (( $(echo "$version >= 3.8" | bc -l) )); then
            echo "$python_cmd"
            return 0
        fi
    fi
    return 1
}

# Find Python
echo "Checking for Python installation..."

PYTHON_CMD=""

# Try python3 first (most common on Linux)
if check_python_version "python3"; then
    PYTHON_CMD="python3"
elif check_python_version "python"; then
    PYTHON_CMD="python"
else
    # Try specific versions
    for ver in {12..8}; do
        if check_python_version "python3.$ver"; then
            PYTHON_CMD="python3.$ver"
            break
        fi
    done
fi

# Check if Python was found
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}ERROR: Python 3.8 or higher not found!${NC}"
    echo
    echo "Please install Python 3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    echo
    exit 1
fi

echo -e "${GREEN}Found Python: $PYTHON_CMD${NC}"

# Check for venv module
if ! "$PYTHON_CMD" -c "import venv" &> /dev/null; then
    echo -e "${YELLOW}WARNING: Python venv module not found${NC}"
    echo "Installing python3-venv..."
    
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-venv
    elif command -v dnf &> /dev/null; then
        sudo dnf install python3-venv
    else
        echo -e "${RED}Please install python3-venv manually${NC}"
        exit 1
    fi
fi

# Check current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo
echo "Starting installation..."
echo

# Run the installer
"$PYTHON_CMD" install_picosync.py

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}====================================="
    echo -e "    Installation Complete!"
    echo -e "=====================================${NC}"
    echo
    echo "You can now run PicoSync by:"
    echo "  - Running: ./run_picosync.sh"
    echo "  - Using the application menu"
    echo
    
    # Make run script executable
    if [ -f "run_picosync.sh" ]; then
        chmod +x run_picosync.sh
    fi
else
    echo
    echo -e "${RED}Installation failed!${NC}"
    echo "Please check the error messages above."
    exit 1
fi