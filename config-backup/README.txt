install uv 
curl -LsSf https://astral.sh/uv/install.sh | sh

powershell -c "irm https://astral.sh/uv/install.ps1 | more"


source pico_venv/bin/activate (activate your virtual environment)

uv pip install -r requirments.txt (installs requirements recursively) 

run installer
uv run python pico_installer.py

run manager 
uv run python pico_sync_manager.py
