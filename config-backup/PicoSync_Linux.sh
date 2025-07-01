#!/bin/bash

# PicoSync Linux Universal Launcher
# Auto-detects Python, sets up environment, and runs the application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PicoSync Linux Launcher ===${NC}"

# Change to script directory
cd "$(dirname "$0")"

# Check if virtual environment exists and is valid
if [ -f "pico_venv/bin/python" ]; then
    echo "Virtual environment found. Launching PicoSync..."
    ./pico_venv/bin/python pico_sync_manager.py "$@"
    exit $?
fi

# Check if PicoSync.sh exists but is incorrect
if [ -f "PicoSync.sh" ]; then
    # Check if it's using the virtual environment
    if ! grep -q "pico_venv" PicoSync.sh; then
        echo "Found outdated PicoSync.sh. Recreating..."
        rm -f PicoSync.sh
    fi
fi

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    if command -v "$python_cmd" &> /dev/null; then
        local version=$("$python_cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 6 ]; then
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
    for ver in {13..6}; do
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
    echo "Would you like to install Python now? (requires sudo)"
    read -p "Install Python? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Detect package manager and install Python
        if command -v apt-get &> /dev/null; then
            echo "Installing Python using apt..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v dnf &> /dev/null; then
            echo "Installing Python using dnf..."
            sudo dnf install -y python3 python3-pip
        elif command -v pacman &> /dev/null; then
            echo "Installing Python using pacman..."
            sudo pacman -S --noconfirm python python-pip
        elif command -v zypper &> /dev/null; then
            echo "Installing Python using zypper..."
            sudo zypper install -y python3 python3-pip
        else
            echo -e "${RED}Could not detect package manager!${NC}"
            echo "Please install Python 3.6+ manually and run this script again."
            exit 1
        fi
        
        # Re-check for Python
        if check_python_version "python3"; then
            PYTHON_CMD="python3"
        else
            echo -e "${RED}Python installation failed!${NC}"
            exit 1
        fi
    else
        echo "Please install Python 3.6+ manually and run this script again."
        exit 1
    fi
fi

echo -e "${GREEN}Found Python: $PYTHON_CMD${NC}"

# Check for pip
if ! "$PYTHON_CMD" -m pip --version &> /dev/null; then
    echo -e "${YELLOW}WARNING: pip not found.${NC}"
    
    # Check if we can install pip
    echo "Would you like to install pip? (requires sudo)"
    read -p "Install pip? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Try to install pip using the package manager
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-pip
        else
            # Try using ensurepip
            echo "Trying to install pip using ensurepip..."
            "$PYTHON_CMD" -m ensurepip --default-pip
        fi
        
        # Verify pip installation
        if ! "$PYTHON_CMD" -m pip --version &> /dev/null; then
            echo -e "${RED}ERROR: Failed to install pip!${NC}"
            exit 1
        fi
    else
        echo -e "${RED}ERROR: pip is required to continue!${NC}"
        exit 1
    fi
fi

# Check for venv module
if ! "$PYTHON_CMD" -c "import venv" &> /dev/null; then
    echo -e "${YELLOW}WARNING: venv module not found.${NC}"
    
    if command -v apt-get &> /dev/null; then
        echo "Installing python3-venv..."
        sudo apt-get install -y python3-venv
    else
        echo -e "${RED}ERROR: venv module is required!${NC}"
        echo "Please install it using your package manager."
        exit 1
    fi
fi

# Check for USB permissions
echo "Checking system configuration..."

if ! groups | grep -q 'dialout'; then
    echo -e "${YELLOW}WARNING: Your user is not in the 'dialout' group.${NC}"
    echo "This is required for USB access to the Pico."
    echo ""
    read -p "Add user to dialout group? (requires sudo) (Y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        sudo usermod -a -G dialout "$USER"
        echo -e "${GREEN}Added user to dialout group.${NC}"
        echo -e "${YELLOW}You must log out and back in for this to take effect!${NC}"
        echo ""
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
fi

# Check if installer exists
if [ ! -f "pico_installer.py" ]; then
    echo -e "${RED}ERROR: pico_installer.py not found!${NC}"
    echo "Please make sure all PicoSync files are in the current directory."
    exit 1
fi

# Run the installer
echo ""
echo "Running PicoSync installer..."
echo "This will set up a virtual environment and install dependencies..."
echo ""

"$PYTHON_CMD" pico_installer.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}Installation successful!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    
    # Create proper PicoSync.sh if it doesn't exist
    if [ ! -f "PicoSync.sh" ]; then
        echo "Creating PicoSync.sh launcher..."
        cat > PicoSync.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"

if [ ! -f "pico_venv/bin/python" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run pico_installer.py first"
    exit 1
fi

./pico_venv/bin/python pico_sync_manager.py "$@"
EOF
        chmod +x PicoSync.sh
    fi
    
    # Launch PicoSync
    if [ -f "pico_venv/bin/python" ]; then
        echo "Launching PicoSync..."
        echo ""
        sleep 2
        ./pico_venv/bin/python pico_sync_manager.py "$@"
    else
        echo -e "${RED}ERROR: Virtual environment not created properly!${NC}"
        exit 1
    fi
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}Installation failed!${NC}"
    echo -e "${RED}=========================================${NC}"
    echo "Please check the error messages above."
    echo ""
    echo "Common issues:"
    echo "- Internet connection required for downloading packages"
    echo "- Missing development packages (python3-dev, build-essential)"
    echo "- Try running with sudo if permission errors occur"
    echo ""
    exit 1
fi