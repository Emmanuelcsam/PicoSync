#!/bin/bash

# PicoSync Linux Launcher
# Auto-detects Python and runs the installer/application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PicoSync Linux Launcher ===${NC}"

# Check if already installed (launcher exists)
if [ -f "PicoSync.sh" ]; then
    echo "PicoSync is already installed. Launching..."
    ./PicoSync.sh "$@"
    exit 0
fi

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    if command -v "$python_cmd" &> /dev/null; then
        local version=$("$python_cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if (( $(echo "$version >= 3.6" | bc -l) )); then
            echo "$python_cmd"
            return 0
        fi
    fi
    return 1
}

# Try to find suitable Python
echo "Detecting Python installation..."

PYTHON_CMD=""

# Try python3 first (most common on Linux)
if check_python_version "python3"; then
    PYTHON_CMD="python3"
# Try python
elif check_python_version "python"; then
    PYTHON_CMD="python"
# Try python3.x versions
else
    for ver in {12..6}; do
        if check_python_version "python3.$ver"; then
            PYTHON_CMD="python3.$ver"
            break
        fi
    done
fi

# Check if Python was found
if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}ERROR: Python 3.6 or higher not found!${NC}"
    echo ""
    echo "Please install Python 3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    echo ""
    exit 1
fi

echo -e "${GREEN}Found Python: $PYTHON_CMD${NC}"

# Check for pip
if ! "$PYTHON_CMD" -m pip --version &> /dev/null; then
    echo -e "${YELLOW}WARNING: pip not found. Installing pip...${NC}"
    
    # Try to install pip using the package manager
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install python3-pip
    elif command -v pacman &> /dev/null; then
        sudo pacman -S python-pip
    else
        echo -e "${RED}Could not install pip automatically. Please install it manually.${NC}"
        exit 1
    fi
fi

# Check for required system packages
echo "Checking system dependencies..."

# Check for USB permissions
if ! groups | grep -q 'dialout'; then
    echo -e "${YELLOW}WARNING: Your user is not in the 'dialout' group.${NC}"
    echo "You may need to run: sudo usermod -a -G dialout $USER"
    echo "Then log out and back in for USB access to work properly."
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the installer
echo ""
echo "Running PicoSync installer..."
"$PYTHON_CMD" pico_installer.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Installation complete!${NC}"
    echo "You can now run ./PicoSync.sh"
    echo ""
    
    # Make the launcher executable
    if [ -f "PicoSync.sh" ]; then
        chmod +x PicoSync.sh
        
        # Ask if user wants to launch now
        read -p "Launch PicoSync now? (Y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            ./PicoSync.sh
        fi
    fi
else
    echo ""
    echo -e "${RED}Installation failed. Please check the error messages above.${NC}"
    exit 1
fi