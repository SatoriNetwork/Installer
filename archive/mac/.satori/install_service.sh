#!/bin/bash

# Script for creating, checking, updating, or removing a .plist file for the neuron.sh script

# Script name and path
SCRIPT_NAME="neuron.sh"
CURRENT_DIR=$(pwd)
SCRIPT_PATH="$CURRENT_DIR/$SCRIPT_NAME"

# .plist file name and path
PLIST_LABEL="com.example.neuron"
PLIST_FILE_NAME="$PLIST_LABEL.plist"
PLIST_FILE="$CURRENT_DIR/$PLIST_FILE_NAME"

# Changing permissions to make neuron.sh executable
chmod +x "$SCRIPT_PATH"

# Check if the service is already registered
if launchctl list | grep -q "$PLIST_LABEL"; then
    echo "The service '$SCRIPT_NAME' is already registered in the startup."
    read -p "Do you want to remove (R), reinstall (I), or do nothing (N)? (R/I/N) " action

    case $action in
        [Rr]* )
            # Unloading and removing the service
            launchctl unload -w "$PLIST_FILE"
            rm "$PLIST_FILE"
            echo "The service '$SCRIPT_NAME' has been removed from startup."
            ;;
        [Ii]* )
            # Reinstalling the service
            launchctl unload -w "$PLIST_FILE"
            launchctl load -w "$PLIST_FILE"
            echo "The service '$SCRIPT_NAME' has been reinstalled."
            ;;
        * )
            echo "No action taken."
            ;;
    esac
else
    # Creating a .plist file for autostarting neuron.sh
    cat << EOF > "$PLIST_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>

    <key>RunAtLoad</key>
    <true/>

    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_PATH</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$CURRENT_DIR</string>

    <key>StandardOutPath</key>
    <string>$CURRENT_DIR/neuron_out.log</string>

    <key>StandardErrorPath</key>
    <string>$CURRENT_DIR/neuron_err.log</string>
</dict>
</plist>
EOF

    echo "The .plist file has been created: $PLIST_FILE"

    # Loading the .plist file into launchd
    launchctl load -w "$PLIST_FILE"
    echo "The service '$SCRIPT_NAME' has been added to the startup."
fi

# Asking whether to run the script now
read -p "Do you want to run the script '$SCRIPT_NAME' now? (Y/N) " answer
if [[ $answer == [Yy]* ]]; then
    "$SCRIPT_PATH"
    echo "The script '$SCRIPT_NAME' has been run."
else
    echo "The script '$SCRIPT_NAME' has not been run."
fi

# Create a desktop shortcut to neuron.sh
DESKTOP_SHORTCUT_PATH="$HOME/Desktop/Start Satori.command"
echo "#!/bin/bash" > "$DESKTOP_SHORTCUT_PATH"
echo "$SCRIPT_PATH" >> "$DESKTOP_SHORTCUT_PATH"
chmod +x "$DESKTOP_SHORTCUT_PATH"
echo "Shortcut 'Start Satori' has been created on the Desktop."
