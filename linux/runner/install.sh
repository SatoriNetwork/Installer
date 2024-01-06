#!/bin/bash

#### Installing Satori in virtual environment with dependencies ####

# make scripts executable
chmod +x satori.sh
chmod +x satori.py

# Create virtual environment
python3 -m venv myenv

# Check if the virtual environment was created successfully
if [ -d "myenv" ]; then
    echo "Virtual environment created successfully."

    # Activate the virtual environment
    source myenv/bin/activate

    # Check if activation was successful
    if [ "$VIRTUAL_ENV" != "" ]; then
        echo "Virtual environment activated."

        # Install requirements
        pip install -r requirements.txt

        echo "Dependencies installed."
    else
        echo "Failed to activate the virtual environment."
    fi
else
    echo "Failed to create virtual environment."
fi


#### Make Satori run on login ####

if [ -n "$BASH_VERSION" ]; then
    # Check for ~/.bash_profile, ~/.bash_login, then ~/.profile
    if [ -f "$HOME/.bash_profile" ]; then
        PROFILE_FILE="$HOME/.bash_profile"
    elif [ -f "$HOME/.bash_login" ]; then
        PROFILE_FILE="$HOME/.bash_login"
    elif [ -f "$HOME/.profile" ]; then
        PROFILE_FILE="$HOME/.profile"
    else
        # If none exist, default to creating ~/.bash_profile
        PROFILE_FILE="$HOME/.bash_profile"
    fi
elif [ -n "$ZSH_VERSION" ]; then
    # For Zsh, check for ~/.zprofile or ~/.profile
    if [ -f "$HOME/.zprofile" ]; then
        PROFILE_FILE="$HOME/.zprofile"
    elif [ -f "$HOME/.profile" ]; then
        PROFILE_FILE="$HOME/.profile"
    else
        # If none exist, default to creating ~/.zprofile
        PROFILE_FILE="$HOME/.zprofile"
    fi
else
    # Default to ~/.profile for other shells
    PROFILE_FILE="$HOME/.profile"
fi

echo "Using profile file: $PROFILE_FILE"
# Here you can append your command to the determined profile file
echo "/path/to/python3 /path/to/your/script.sh" >> "$PROFILE_FILE"
