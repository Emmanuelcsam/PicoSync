#!/bin/bash

# PicoSync Linux Runner
# Runs PicoSync with proper environment

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if installed
if [ ! -f "picosync_config.json" ]; then
    echo -e "${RED}ERROR: PicoSync is not installed!${NC}"
    echo
    echo "Please run the installer first:"
    echo "  ./install_picosync.sh"
    echo
    exit 1
fi

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
PYTHON_CMD=""

# Try python3 first
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
    echo -e "${RED}ERROR: Python not found!${NC}"
    echo "Please ensure Python is installed"
    exit 1
fi

# Run the application
"$PYTHON_CMD" run_picosync.py

# Check exit code
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}PicoSync exited with an error.${NC}"
    exit 1
fi