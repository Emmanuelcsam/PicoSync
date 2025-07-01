#!/usr/bin/env python3
# Universal installation shortcut for PicoSync
# References icon from backend/config/core/install.ico

import os
import sys
import subprocess

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Run the installation script from backend
install_script = os.path.join(script_dir, 'backend', 'install_picosync.py')
subprocess.run([sys.executable, install_script])