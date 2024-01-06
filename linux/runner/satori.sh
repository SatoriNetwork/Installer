#!/bin/bash

# Absolute path to the directory of this script
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="~/.satori"
# Path to the virtual environment
VENV_PATH="$DIR/satori"
# Check if the virtual environment directory exists
if [ -d "$VENV_PATH" ]; then
    # Activate the virtual environment
    # Using '.' instead of 'source' for better compatibility with different shells
    . "$VENV_PATH/bin/activate"
    # Check if the virtual environment is activated
    if [ "$VIRTUAL_ENV" = "$VENV_PATH" ]; then
        echo "Virtual environment activated."
        # Run your Python script
        python "$DIR/satori.py"
        # Deactivate the virtual environment
        deactivate
    else
        echo "Failed to activate the virtual environment."
        exit 1
    fi
else
    echo "Virtual environment directory not found."
    exit 1
fi

# check for shell
#if [ -z "$PS1" ]; then
#    return
#fi
# Activate virtual environment
#source /path/to/virtualenv/bin/activate
# Run Python script
#/path/to/virtualenv/bin/python ~/.satori/satori.py
