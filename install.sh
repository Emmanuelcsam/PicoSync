#!/bin/bash
# Universal installation shortcut for PicoSync
# References icon from backend/config/core/install.ico

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the installation script from backend
cd "$SCRIPT_DIR/backend" && ./install_picosync.sh