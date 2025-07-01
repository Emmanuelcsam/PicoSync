https://micropython.org/download/RPI_PICO2/

Requirements
Pico2 .uf2 file
mpremote (MicroPython remote tool)
uv pip install mpremote --system

GitBash
For Setup and Troubleshooting
###You can skip this if you have all the requirements just run ./flash.sh###
###Right Click Folder and Open Terminal###
---------------
chmod +x setup.sh
./setup.sh

Follow setup steps 
------------------
Quick flashing:
-----------
chmod +x flash.sh

./flash.sh

------
chmod +x test.sh

./test.sh

mpremote connect auto ls

-----------------------
Check if connected (via terminal)
-----------------------
mpremote connect list

### Looks like COM5 17D3C3249AC4EE7C 2e8a:0005 Microsoft None

Unplug the Pico completely
Wait 5 seconds
Plug it back in (WITHOUT holding BOOTSEL)
Wait 3 seconds for Windows to recognize it

mpremote connect auto ls # See files inside


----------------------------
Alternative IDE https://thonny.org/

