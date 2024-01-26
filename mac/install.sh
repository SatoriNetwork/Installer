#!/bin/bash

#### Installing Satori in a virtual environment with dependencies ####

# Displaying installation steps
set -x

if [ -f "./neuron.sh" ]; then
    # Making scripts executable
    chmod +x ./neuron.sh
    chmod +x ./satori.py

    # Checking if Python 3 is installed
    command -v python3 >/dev/null 2>&1 || { echo "Python 3 not found, please install Python 3"; exit 1; }

    # Creating a virtual environment
    python3 -m venv "./satorienv"

    # Checking if the virtual environment was created successfully
    if [ -d "./satorienv" ]; then
        echo "Virtual environment created successfully."

        # Activating the virtual environment
        # Using '.' instead of 'source' for better compatibility with different shells
        . "./satorienv/bin/activate"

        # Checking if activation was successful
        if [ "$VIRTUAL_ENV" != "" ]; then
            echo "Virtual environment activated."

            # Installing dependencies
            pip install -r "./requirements.txt"
            echo "Dependencies installed."
        else
            echo "Failed to activate the virtual environment."
        fi
    else
        echo "Failed to create the virtual environment."
    fi
else
    echo ".satori folder not found. Please unzip the Satori archive first."
fi

# Disabling the display of installation steps
set +x

