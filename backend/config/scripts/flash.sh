#!/usr/bin/env bash

set -euo pipefail
read -rp "File or Directory Path: " TARGET

TARGET="${TARGET#\"}"
TARGET="${TARGET%\"}"
TARGET="${TARGET#\'}"
TARGET="${TARGET%\'}"

if [[ "$TARGET" =~ ^([A-Za-z]):\\(.+) ]]; then
  DRIVE="${BASH_REMATCH[1],,}"
  REST="${BASH_REMATCH[2]//\\//}"
  TARGET="/$DRIVE/$REST"
fi

if ! command -v mpremote &>/dev/null; then
  if command -v pip &>/dev/null; then
    pip install --user mpremote
  elif command -v python3 &>/dev/null; then
    python3 -m pip install --user mpremote
  else
    echo "[ERROR] pip or python3 not found"
    exit 1
  fi
fi

if ! mpremote connect list | grep -q .; then
  echo "[ERROR] No Raspberry Pi Pico detected"
  exit 1
fi

if [[ -d "$TARGET" ]]; then
  mpremote connect auto fs cp -r "$TARGET" :
else
  mpremote connect auto fs cp "$TARGET" :
fi

mpremote connect auto reset

echo "[SUCCESS] Deployed '$TARGET' and reset Pico"
