#!/bin/bash
# This script launches the Python script in a new Terminal window

# Path to the Python script inside the app bundle
PYTHON_SCRIPT_PATH="$(dirname "$0")/Satori"

# Command to open Terminal and run the Python script
osascript -e "tell application \"Terminal\" to do script \"$PYTHON_SCRIPT_PATH\""
