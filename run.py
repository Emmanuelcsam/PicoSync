#!/usr/bin/env python3
# Universal run shortcut for PicoSync
# References icon from backend/config/core/run.ico

import os
import sys
import subprocess

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Run the application from backend
run_script = os.path.join(script_dir, 'backend', 'run_picosync.py')
subprocess.run([sys.executable, run_script])