#!/bin/bash
# Universal run shortcut for PicoSync
# References icon from backend/config/core/run.ico

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the application from backend
cd "$SCRIPT_DIR/backend" && ./run_picosync.sh