cd /c/Users/Saem1001/Desktop/pico_setup/Pico_pi_files
for file in *.py; do
    echo "Copying $file..."
    mpremote connect auto cp "$file" :
done
