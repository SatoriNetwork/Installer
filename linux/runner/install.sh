#!/bin/bash

#### Installing Satori in virtual environment with dependencies ####

# make scripts executable
chmod +x satori.sh
chmod +x satori.py
# Create virtual environment
command -v python3 >/dev/null 2>&1 || { echo "Python 3 not found, please install Python 3"; exit 1; }
python3 -m venv "$HOME/.satori/env"
# Check if the virtual environment was created successfully
if [ -d "$HOME/.satori/env" ]; then
    echo "Virtual environment created successfully."
    # Activate the virtual environment
    source "$HOME/.satori/env/bin/activate"
    # Check if activation was successful
    if [ "$VIRTUAL_ENV" != "" ]; then
        echo "Virtual environment activated."
        pip install -r "$HOME/.satori/requirements.txt"
        echo "Dependencies installed."
    else
        echo "Failed to activate the virtual environment."
    fi
else
    echo "Failed to create virtual environment."
fi
