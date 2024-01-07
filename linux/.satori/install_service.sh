#!/bin/bash

# Script to update satori.service with correct user, group, and ExecStart

CURRENT_DIR=$(pwd)
SERVICE_FILE="$CURRENT_DIR/satori.service"
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)
#HOME_DIR=$(eval echo ~$CURRENT_USER)

# Updating the User and Group in the satori.service file
sed -i "s/#User=.*/User=$CURRENT_USER/" $SERVICE_FILE
sed -i "s/#Group=.*/Group=$CURRENT_GROUP/" $SERVICE_FILE

# Updating the WorkingDirectory path
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_DIR|" $SERVICE_FILE

echo "satori.service has been updated with User, Group, and ExecStart path."
