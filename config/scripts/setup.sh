#!/usr/bin/env bash
# flash_pico.sh - Enhanced version for Git Bash on Windows with Pico & Pico 2 support

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Global variables
DETECTED_MODEL=""
BOOT_MOUNT=""

# Detect username dynamically
if [ -n "${USERNAME:-}" ]; then
    CURRENT_USER="$USERNAME"
elif [ -n "${USER:-}" ]; then
    CURRENT_USER="$USER"
else
    CURRENT_USER="YourUsername"
fi

print_status() { echo -e "${BLUE}[STATUS]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Convert Windows path to Git Bash path
convert_windows_path() {
    local path="$1"
    
    # Remove quotes if present
    path="${path%\"}"
    path="${path#\"}"
    
    # Check if it's a Windows path (contains : or \)
    if [[ "$path" =~ ^[A-Za-z]: ]] || [[ "$path" =~ \\ ]]; then
        # Convert backslashes to forward slashes
        path="${path//\\//}"
        
        # Convert C: to /c/, D: to /d/, etc.
        if [[ "$path" =~ ^[A-Za-z]: ]]; then
            drive="${path:0:1}"
            drive_lower=$(echo "$drive" | tr '[:upper:]' '[:lower:]')
            path="/${drive_lower}${path:2}"
        fi
    fi
    
    echo "$path"
}

# Function to find RPI-RP2 drive on Windows
find_rpi_drive() {
    # On Windows, drives are at /c/, /d/, etc. in Git Bash
    for letter in {a..z}; do
        drive="/${letter}"
        if [ -d "$drive" ]; then
            # Check if INFO_UF2.TXT exists (indicator of BOOTSEL mode)
            if [ -f "${drive}/INFO_UF2.TXT" ]; then
                BOOT_MOUNT="$drive"
                # Try to detect which model
                if grep -q "RP2350" "${drive}/INFO_UF2.TXT" 2>/dev/null; then
                    DETECTED_MODEL="Pico 2 (RP2350)"
                elif grep -q "RP2040" "${drive}/INFO_UF2.TXT" 2>/dev/null; then
                    DETECTED_MODEL="Original Pico (RP2040)"
                else
                    DETECTED_MODEL="Unknown Pico model"
                fi
                return 0
            fi
        fi
    done
    return 1
}

# Wait for BOOTSEL with Windows-specific detection
wait_for_bootsel() {
    print_status "Waiting for Raspberry Pi Pico in BOOTSEL mode..."
    print_warning "Make sure you:"
    echo "  1. Unplugged the Pico"
    echo "  2. Are holding the BOOTSEL button"
    echo "  3. Plug in the USB while holding BOOTSEL"
    echo "  4. Wait 2 seconds then release BOOTSEL"
    
    local attempts=0
    while [ $attempts -lt 60 ]; do
        if find_rpi_drive; then
            print_success "Found BOOTSEL drive at: $BOOT_MOUNT (Windows drive ${BOOT_MOUNT:1:1}:)"
            if [ -n "${DETECTED_MODEL:-}" ]; then
                print_success "Detected model: $DETECTED_MODEL"
            fi
            return 0
        fi
        
        if [ $((attempts % 10)) -eq 0 ] && [ $attempts -gt 0 ]; then
            print_status "Still waiting... (${attempts}s)"
        fi
        
        sleep 1
        ((attempts++))
    done
    
    print_error "Timeout! Could not find RPI-RP2 drive"
    return 1
}

# Function to safely read path input
read_path() {
    local prompt="$1"
    local input_path
    
    # Send prompt to stderr so it doesn't get captured
    echo -n "$prompt" >&2
    read -r input_path
    
    # Remove quotes if present
    input_path="${input_path%\"}"
    input_path="${input_path#\"}"
    
    # Convert Windows path to Git Bash format
    local converted_path=$(convert_windows_path "$input_path")
    
    # Show the conversion if it happened (to stderr)
    if [ "$input_path" != "$converted_path" ]; then
        print_status "Converted path to: $converted_path" >&2
    fi
    
    # Only output the converted path to stdout
    echo "$converted_path"
}


# Quick detection if Pico is already in BOOTSEL
if find_rpi_drive 2>/dev/null; then
    print_success "Detected Pico in BOOTSEL mode: $DETECTED_MODEL"
    echo
fi

print_status "What would you like to do?"
echo "1) Complete setup (download MicroPython, flash, and copy files)"
echo "2) Just flash MicroPython (I already have the .uf2 file)"
echo "3) Just copy files (MicroPython already installed)"
echo "4) Quick fix: Download and flash Pico 2 firmware (if you used wrong firmware)"
echo -n "Enter your choice (1-4): "
read -r CHOICE

case $CHOICE in
    1|2|4)
        if [ "$CHOICE" = "4" ]; then
            # Quick fix for Pico 2
            FIRMWARE_URL="https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
            FIRMWARE_FILE="RPI_PICO2-latest.uf2"
            
            print_status "Downloading Pico 2 (RP2350) MicroPython firmware..."
            if command -v curl &>/dev/null; then
                curl -L -o "$FIRMWARE_FILE" "$FIRMWARE_URL" || {
                    print_error "Failed to download"
                    exit 1
                }
            else
                powershell -Command "Invoke-WebRequest -Uri '$FIRMWARE_URL' -OutFile '$FIRMWARE_FILE'" || {
                    print_error "Failed to download"
                    exit 1
                }
            fi
            print_success "Downloaded $FIRMWARE_FILE"
        elif [ "$CHOICE" = "1" ]; then
            print_status "Do you want to download the latest MicroPython?"
            echo -n "Enter Y for yes, N to use existing file: "
            read -r DOWNLOAD_CHOICE
            
            if [[ $DOWNLOAD_CHOICE =~ ^[Yy]$ ]]; then
                echo
                print_status "Which Raspberry Pi Pico model do you have?"
                
                # Check if we already detected a model in BOOTSEL
                if [ -n "$DETECTED_MODEL" ] && [[ "$DETECTED_MODEL" != "Unknown"* ]]; then
                    print_success "Auto-detected: $DETECTED_MODEL"
                    echo -n "Use detected model? (Y/n): "
                    read -r USE_DETECTED
                    if [[ ! $USE_DETECTED =~ ^[Nn]$ ]]; then
                        if [[ "$DETECTED_MODEL" == *"RP2350"* ]]; then
                            PICO_MODEL=2
                        else
                            PICO_MODEL=1
                        fi
                    else
                        PICO_MODEL=""
                    fi
                fi
                
                if [ -z "${PICO_MODEL:-}" ]; then
                    echo "1) Pico (original with RP2040 chip)"
                    echo "2) Pico 2 (newer with RP2350 chip)"
                    echo
                    print_warning "To check: Put Pico in BOOTSEL mode and look at INFO_UF2.TXT"
                    echo "  - RP2040 = Original Pico"
                    echo "  - RP2350 = Pico 2"
                    echo -n "Enter your choice (1-2): "
                    read -r PICO_MODEL
                fi
                
                case $PICO_MODEL in
                    1)
                        FIRMWARE_URL="https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2"
                        FIRMWARE_FILE="RPI_PICO-latest.uf2"
                        print_status "Selected: Original Pico (RP2040)"
                        ;;
                    2)
                        FIRMWARE_URL="https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
                        FIRMWARE_FILE="RPI_PICO2-latest.uf2"
                        print_status "Selected: Pico 2 (RP2350)"
                        ;;
                    *)
                        print_error "Invalid choice. Defaulting to original Pico"
                        FIRMWARE_URL="https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2"
                        FIRMWARE_FILE="RPI_PICO-latest.uf2"
                        ;;
                esac
                
                echo
                print_status "Downloading MicroPython for your Pico..."
                if command -v curl &>/dev/null; then
                    curl -L -o "$FIRMWARE_FILE" "$FIRMWARE_URL" || {
                        print_error "Failed to download"
                        exit 1
                    }
                else
                    powershell -Command "Invoke-WebRequest -Uri '$FIRMWARE_URL' -OutFile '$FIRMWARE_FILE'" || {
                        print_error "Failed to download"
                        exit 1
                    }
                fi
                print_success "Downloaded $FIRMWARE_FILE"
            else
                print_warning "Firmware file naming:"
                echo "  - Original Pico: RPI_PICO-xxx.uf2"
                echo "  - Pico 2: RPI_PICO2-xxx.uf2"
                FIRMWARE_FILE=$(read_path "Enter the path to your .uf2 file: ")
                if [ ! -f "$FIRMWARE_FILE" ]; then
                    print_error "File not found: $FIRMWARE_FILE"
                    print_warning "Make sure the path is correct. You can use:"
                    echo "  - Windows paths: C:\\Users\\file.uf2"
                    echo "  - Git Bash paths: /c/Users/file.uf2"
                    echo "  - Relative paths: ./file.uf2"
                    exit 1
                fi
            fi
        else
            print_warning "Firmware file naming:"
            echo "  - Original Pico: RPI_PICO-xxx.uf2"
            echo "  - Pico 2: RPI_PICO2-xxx.uf2"
            FIRMWARE_FILE=$(read_path "Enter the path to your .uf2 file: ")
            if [ ! -f "$FIRMWARE_FILE" ]; then
                print_error "File not found: $FIRMWARE_FILE"
                print_warning "Make sure the path is correct. You can use:"
                echo "  - Windows paths: C:\\Users\\file.uf2"
                echo "  - Git Bash paths: /c/Users/file.uf2"
                echo "  - Relative paths: ./file.uf2"
                exit 1
            fi
        fi
        
        echo
        print_warning "Time to put Pico in BOOTSEL mode!"
        echo "1) Unplug your Pico completely"
        echo "2) Press and HOLD the white BOOTSEL button"
        echo "3) While holding BOOTSEL, plug in the USB cable"
        echo "4) Count to 2, then release BOOTSEL"
        echo
        echo -n "Press Enter when ready..."
        read -r
        
        if wait_for_bootsel; then
            # Check if firmware matches detected model
            if [ -n "${DETECTED_MODEL:-}" ]; then
                if [[ "$DETECTED_MODEL" == *"RP2350"* ]] && [[ "$FIRMWARE_FILE" == *"RPI_PICO-"* ]] && [[ "$FIRMWARE_FILE" != *"PICO2"* ]]; then
                    print_warning "You have a Pico 2 (RP2350) but selected firmware for original Pico!"
                    echo -n "Download correct firmware now? (Y/n): "
                    read -r DOWNLOAD_CORRECT
                    if [[ ! $DOWNLOAD_CORRECT =~ ^[Nn]$ ]]; then
                        FIRMWARE_URL="https://micropython.org/download/RPI_PICO2/RPI_PICO2-latest.uf2"
                        FIRMWARE_FILE="RPI_PICO2-latest.uf2"
                        print_status "Downloading correct firmware..."
                        if command -v curl &>/dev/null; then
                            curl -L -o "$FIRMWARE_FILE" "$FIRMWARE_URL" || {
                                print_error "Failed to download"
                                exit 1
                            }
                        else
                            powershell -Command "Invoke-WebRequest -Uri '$FIRMWARE_URL' -OutFile '$FIRMWARE_FILE'" || {
                                print_error "Failed to download"
                                exit 1
                            }
                        fi
                        print_success "Downloaded correct firmware: $FIRMWARE_FILE"
                    else
                        echo -n "Continue with wrong firmware anyway? (y/N): "
                        read -r CONTINUE
                        if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
                            print_warning "Cancelled. Please run again with correct firmware."
                            exit 1
                        fi
                    fi
                elif [[ "$DETECTED_MODEL" == *"RP2040"* ]] && [[ "$FIRMWARE_FILE" == *"PICO2"* ]]; then
                    print_warning "You have an original Pico (RP2040) but selected Pico 2 firmware!"
                    echo -n "Download correct firmware now? (Y/n): "
                    read -r DOWNLOAD_CORRECT
                    if [[ ! $DOWNLOAD_CORRECT =~ ^[Nn]$ ]]; then
                        FIRMWARE_URL="https://micropython.org/download/RPI_PICO/RPI_PICO-latest.uf2"
                        FIRMWARE_FILE="RPI_PICO-latest.uf2"
                        print_status "Downloading correct firmware..."
                        if command -v curl &>/dev/null; then
                            curl -L -o "$FIRMWARE_FILE" "$FIRMWARE_URL" || {
                                print_error "Failed to download"
                                exit 1
                            }
                        else
                            powershell -Command "Invoke-WebRequest -Uri '$FIRMWARE_URL' -OutFile '$FIRMWARE_FILE'" || {
                                print_error "Failed to download"
                                exit 1
                            }
                        fi
                        print_success "Downloaded correct firmware: $FIRMWARE_FILE"
                    else
                        echo -n "Continue with wrong firmware anyway? (y/N): "
                        read -r CONTINUE
                        if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
                            print_warning "Cancelled. Please run again with correct firmware."
                            exit 1
                        fi
                    fi
                fi
            fi
            
            print_status "Copying firmware to Pico..."
            cp "$FIRMWARE_FILE" "$BOOT_MOUNT/" || {
                print_error "Failed to copy firmware"
                exit 1
            }
            
            # Force sync to ensure write is complete
            sync
            
            print_success "Firmware copied!"
            echo
            print_warning "The Pico should reboot automatically in a few seconds."
            print_warning "If it doesn't reboot:"
            echo "  1. Unplug the Pico"
            echo "  2. Wait 2 seconds"
            echo "  3. Plug it back in (WITHOUT holding BOOTSEL)"
            echo
            
            # Wait a bit for auto-reboot
            print_status "Waiting for automatic reboot..."
            sleep 5
            
            # Check if still in BOOTSEL mode
            if find_rpi_drive 2>/dev/null; then
                print_warning "Pico still in BOOTSEL mode!"
                echo
                print_warning "Please manually unplug and replug the Pico (without BOOTSEL)"
                echo -n "Press Enter after you've done this..."
                read -r
            fi
            
            print_success "MicroPython firmware installed!"
        else
            print_error "Could not detect Pico in BOOTSEL mode"
            exit 1
        fi
        ;;
esac

# File copying section
if [ "$CHOICE" = "3" ] || ([ "$CHOICE" = "1" ] && [ -n "${FIRMWARE_FILE:-}" ]); then
    echo
    print_status "Do you want to copy files to the Pico?"
    echo -n "Enter Y for yes, N to skip: "
    read -r COPY_CHOICE
    
    if [[ $COPY_CHOICE =~ ^[Yy]$ ]]; then
        print_warning "Note: Standard MicroPython requires 'mpremote' tool for file transfer"
        
        # Check if mpremote exists
        if command -v mpremote &>/dev/null; then
            print_success "Found mpremote!"
        else
            print_warning "mpremote not found. Trying to install it..."
            
            # Try to install mpremote
            if command -v pip &>/dev/null; then
                pip install mpremote
            elif command -v python &>/dev/null; then
                python -m pip install mpremote
            elif command -v python3 &>/dev/null; then
                python3 -m pip install mpremote
            else
                print_error "Python/pip not found. Please install Python first."
                print_warning "You can download Python from: https://www.python.org/"
                exit 1
            fi
            
            # Check again
            if ! command -v mpremote &>/dev/null; then
                print_error "Failed to install mpremote"
                print_warning "Try running in a new terminal: pip install mpremote"
                exit 1
            fi
        fi
        
        echo
        print_status "What do you want to copy?"
        echo "1) A single file"
        echo "2) An entire directory"
        echo "3) All .py files in current directory"
        echo -n "Enter your choice (1-3): "
        read -r COPY_TYPE
        
        case $COPY_TYPE in
            1)
                FILE_PATH=$(read_path "Enter the file path: ")
                if [ ! -f "$FILE_PATH" ]; then
                    print_error "File not found: $FILE_PATH"
                    print_warning "Tip: You can use Windows or Unix paths:"
                    echo "  Windows: C:\\Users\\$CURRENT_USER\\file.py"
                    echo "  Unix: /c/Users/$CURRENT_USER/file.py"
                    exit 1
                fi
                FILES_TO_COPY=("$FILE_PATH")
                ;;
            2)
                # Show current directory and available directories FIRST
                print_status "Current directory: $(pwd)"
                print_status "Available directories here:"
                ls -d */ 2>/dev/null | sed 's/^/  /' || echo "  (no directories found)"
                echo
                
                print_warning "Path examples based on what's available:"
                # Show example with actual directory if it exists
                if [ -d "Pico_pi_files" ]; then
                    echo "  For Pico_pi_files/ shown above, just type: Pico_pi_files"
                    echo "  Or: ./Pico_pi_files"
                elif ls -d */ 2>/dev/null | head -1 >/dev/null; then
                    # If there's at least one directory, show example with the first one
                    FIRST_DIR=$(ls -d */ 2>/dev/null | head -1 | sed 's/\///')
                    echo "  For $FIRST_DIR/ shown above, just type: $FIRST_DIR"
                    echo "  Or: ./$FIRST_DIR"
                fi
                echo "  Full Windows path: C:\\Users\\$CURRENT_USER\\Desktop\\your_folder"
                echo "  Full Unix path: /c/Users/$CURRENT_USER/Desktop/your_folder"
                echo
                
                DIR_PATH=$(read_path "Enter the directory path: ")
                
                # If directory not found, try some alternatives
                if [ ! -d "$DIR_PATH" ]; then
                    # Try just the basename in case they gave full path to current dir
                    basename_path=$(basename "$DIR_PATH")
                    if [ -d "$basename_path" ]; then
                        print_warning "Found directory locally: ./$basename_path"
                        DIR_PATH="./$basename_path"
                    else
                        print_error "Directory not found: $DIR_PATH"
                        
                        # Show what we tried
                        if [ "$basename_path" != "$DIR_PATH" ]; then
                            print_warning "Also tried: ./$basename_path"
                        fi
                        
                        # Show nearby directories again
                        print_warning "Available directories in current location:"
                        ls -d */ 2>/dev/null | head -10 || echo "  (no directories found)"
                        
                        # Check if the target exists but is a file
                        if [ -f "$DIR_PATH" ]; then
                            print_warning "Note: '$DIR_PATH' is a file, not a directory"
                        fi
                        
                        # Check parent directory
                        parent_dir=$(dirname "$DIR_PATH")
                        if [ -d "$parent_dir" ] && [ "$parent_dir" != "." ]; then
                            print_warning "Parent directory exists: $parent_dir"
                            print_warning "Contents of parent:"
                            ls -d "$parent_dir"/*/ 2>/dev/null | head -5 || echo "  (no subdirectories)"
                        fi
                        
                        exit 1
                    fi
                fi
                
                # Find all files (not directories)
                print_status "Scanning directory for files..."
                mapfile -t FILES_TO_COPY < <(find "$DIR_PATH" -type f 2>/dev/null)
                
                if [ ${#FILES_TO_COPY[@]} -eq 0 ]; then
                    print_warning "No files found in directory: $DIR_PATH"
                    print_warning "Directory contents:"
                    ls -la "$DIR_PATH" | head -10
                    exit 0
                fi
                
                print_success "Found ${#FILES_TO_COPY[@]} files to copy:"
                for file in "${FILES_TO_COPY[@]:0:5}"; do
                    echo "  - $(basename "$file")"
                done
                if [ ${#FILES_TO_COPY[@]} -gt 5 ]; then
                    echo "  ... and $((${#FILES_TO_COPY[@]} - 5)) more files"
                fi
                echo
                ;;
            3)
                mapfile -t FILES_TO_COPY < <(find . -maxdepth 1 -name "*.py" -type f)
                if [ ${#FILES_TO_COPY[@]} -eq 0 ]; then
                    print_warning "No .py files found in current directory"
                    exit 0
                fi
                print_status "Found ${#FILES_TO_COPY[@]} .py files"
                ;;
        esac
        
        if [ ${#FILES_TO_COPY[@]} -gt 10 ]; then
            echo
            echo -n "Copy all ${#FILES_TO_COPY[@]} files? (Y/N): "
            read -r CONFIRM
            if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
                print_warning "Cancelled"
                exit 0
            fi
        fi
        
        print_status "Copying files with mpremote..."
        print_status "Using COM port auto-detection..."
        
        # Test connection first
        if ! mpremote connect auto ls >/dev/null 2>&1; then
            print_error "Cannot connect to Pico!"
            print_warning "Please check:"
            echo "  1. Pico is connected via USB"
            echo "  2. Pico is NOT in BOOTSEL mode"
            echo "  3. MicroPython is installed on the Pico"
            echo "  4. You're using the correct firmware:"
            echo "     - Original Pico (RP2040): RPI_PICO-xxx.uf2"
            echo "     - Pico 2 (RP2350): RPI_PICO2-xxx.uf2"
            echo
            echo "If you have a Pico 2 and used wrong firmware, reflash with RPI_PICO2-latest.uf2"
            exit 1
        fi
        
        # Count successful copies
        success_count=0
        fail_count=0
        
        for file in "${FILES_TO_COPY[@]}"; do
            # Get just the filename for display
            filename=$(basename "$file")
            echo -n "  Copying: $filename ... "
            
            if mpremote connect auto cp "$file" : 2>/dev/null; then
                echo "✓"
                ((success_count++))
            else
                echo "✗"
                ((fail_count++))
            fi
        done
        
        echo
        if [ $fail_count -gt 0 ]; then
            print_warning "Failed to copy $fail_count file(s)"
            print_warning "Make sure the Pico is running MicroPython (not in BOOTSEL mode)"
            print_warning "Try unplugging and replugging the Pico"
        fi
        
        if [ $success_count -gt 0 ]; then
            print_success "Successfully copied $success_count file(s)"
            
            echo
            echo -n "Reset Pico to run the code? (Y/N): "
            read -r RESET_CHOICE
            if [[ $RESET_CHOICE =~ ^[Yy]$ ]]; then
                if mpremote connect auto reset 2>/dev/null; then
                    print_success "Pico reset!"
                else
                    print_warning "Could not reset - try unplugging and replugging"
                fi
            fi
        fi
    fi
fi

echo
print_success "Done!"
echo
print_status "Tips for using your Pico:"
echo "  • Connect to REPL: mpremote connect auto repl"
echo "  • Copy a file: mpremote connect auto cp yourfile.py :"
echo "  • List files: mpremote connect auto ls"
echo "  • Run a file: mpremote connect auto run yourfile.py"
echo
print_status "Troubleshooting:"
echo "  • If mpremote can't connect, check Device Manager for the COM port"
echo "  • Make sure Pico is NOT in BOOTSEL mode for file operations"
echo "  • On Windows, use Ctrl+] to exit the REPL"
echo
print_status "Model Information:"
echo "  • Original Pico: RP2040 chip, uses RPI_PICO-xxx.uf2 firmware"
echo "  • Pico 2: RP2350 chip, uses RPI_PICO2-xxx.uf2 firmware"
echo "  • Wrong firmware = no serial connection!"