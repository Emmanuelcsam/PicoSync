#!/usr/bin/env bash
# flash_only.sh - Simple script to flash MicroPython firmware to Raspberry Pi Pico

set -euo pipefail

# Color constants 33[0m
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status()  { echo -e "${BLUE}[STATUS]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Find BOOTSEL drive where Pico is mounted
find_boot_drive() {
  for d in /mnt/* /media/*; do
    if [[ -f "$d/INFO_UF2.TXT" ]]; then
      echo "$d"; return 0
    fi
  done
  return 1
}

# Wait until Pico in BOOTSEL mode is detected
wait_for_bootsel() {
  print_status "Please connect your Pico in BOOTSEL mode (hold BOOTSEL button while plugging in)..."
  for i in {1..60}; do
    if d=$(find_boot_drive); then
      print_success "Detected BOOTSEL drive at: $d"
      echo "$d"
      return 0
    fi
    sleep 1
  done
  print_error "Timed out waiting for BOOTSEL drive"
}

# Download and flash firmware
flash_firmware() {
  print_status "Select Pico model to flash MicroPython:" 
  echo " 1) Original Pico (RP2040)"
  echo " 2) Pico 2 (RP2350)"
  read -rp "Choice [1-2]: " choice

  case "$choice" in
    1) URL="https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2";;
    2) URL="https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2";;
    *) print_error "Invalid selection";;
  esac

  FILENAME="${URL##*/}"
  print_status "Downloading firmware: $FILENAME"
  if command -v curl &>/dev/null; then
    curl -L -o "$FILENAME" "$URL"
  else
    wget -O "$FILENAME" "$URL"
  fi
  print_success "Downloaded $FILENAME"

  BOOT=$(wait_for_bootsel)
  print_status "Flashing firmware to Pico..."
  cp "$FILENAME" "$BOOT/" && sync
  print_success "Firmware flashed successfully"
}

# Main
flash_firmware
