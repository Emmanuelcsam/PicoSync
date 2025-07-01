#!/usr/bin/env bash
# wipe_pico2.sh - Factory reset for Raspberry Pi Pico 2

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[STATUS]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Ensure mpremote is installed
print_status "Checking for mpremote..."
if ! command -v mpremote &>/dev/null; then
    print_status "mpremote not found. Installing via pip..."
    if command -v pip &>/dev/null; then
        pip install mpremote || { print_error "Failed to install mpremote"; exit 1; }
    elif command -v python3 &>/dev/null; then
        python3 -m pip install mpremote || { print_error "Failed to install mpremote"; exit 1; }
    else
        print_error "pip or python3 not found. Please install Python and pip first."; exit 1;
    fi
    print_success "mpremote installed"
fi

# Verify Pico is connected (normal mode, not BOOTSEL)
print_status "Detecting Pico on serial port..."
if ! mpremote connect list | grep -q .; then
    print_error "No Raspberry Pi Pico detected. Ensure it's plugged in and not in BOOTSEL mode."; exit 1;
fi
print_success "Pico detected"

# Wipe filesystem
print_status "Wiping Pico filesystem (removing all files)..."
mpremote connect auto rm -rv :/ || { print_error "Failed to wipe filesystem"; exit 1; }
print_success "Filesystem wiped"

# Reset device to apply changes
print_status "Resetting Pico..."
mpremote connect auto reset || { print_error "Reset failed"; exit 1; }
print_success "Pico factory reset complete"
