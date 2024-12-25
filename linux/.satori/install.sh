#!/bin/bash

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

welcome() {
    local local_url="http://localhost:24601"
    echo "
                                      @@@@
                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@         @@@@@@@@@   @@@@@@@@
             @@@@@@@@@@@@@                          @@@@@  @@@@@@@
          @@@@@@@@@@@@                                   @@@ @@@@@@@@
        @@@@@@@@@@                                          @@@@@@@@@@@
      @@@@@@@@@@                                               @@@@@@@@@@
     @@@@@@@@                                                    @@@@@@@@@
   @@@@@@@@@                                                       @ @@@@@@
  @@@@@@@@                                                          @@@@@@@@@
 @@@@@@@@                                                            @ @@@@@@
 @@@@@@@@                                                               @@@@@@
@@@@@@@@                                                                 @@@@@@
@@@@@@@@                                                                 @@@@@@
@@@@@@@                                                                   @ @@@
@@@@@@@                                                                   @ @@@
@@@@@@@                                 @                                @@ @@@
@@@@@@@@                              @@@@@                              @@ @@@
@@@@@@@@                             @@@@@@@                            @@ @@@@
 @@@@@@@@                            @@@@@@@                           @@ @@@
  @@@@@@@@                            @@@@@                           @@ @@@
   @@@@@@@@                        @@@@@@@@@@@                       @@ @@@
    @@@@@@@@@                    @@@@@@@@@@@@@@@                     @ @@@
     @@@@@@@@@@                  @@@@@@@@@@@@@@@                    @ @@@
       @@@@@@@@@@               @@@ @@@@@@@@@ @@@                    @@@
         @@@@@@@@@@@            @@@ @@@@@@@@@ @@@                   @@
           @@@@@@@@@@@@   @@@@@@@@@@@@@@@@@@@@@@@@@@@@             @
              @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      @@
                @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ @@@@@ @
                     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                           @@@@@@@@@@@@@@@@@@@@@@@@@@@

###############################################################################
####                                                                       ####
####                      Starting the Satori Neuron                       ####
####                                                                       ####
####     Please don't close this window or the Satori Neuron will stop.    ####
####           The Satori UI will open in your web browser soon.           ####
####                                                                       ####
####                        $local_url                         ####
####                                                                       ####
###############################################################################

Please make sure that Docker is already running.
And hold tight, this may take several minutes...

"
}

setup_directory() {
    # Define the install directory
    local INSTALL_DIR="$HOME/.satori"
    # Create the necessary directories if they don't already exist
    mkdir -p "$INSTALL_DIR/wallet"
    mkdir -p "$INSTALL_DIR/config"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/models"
    log "Directories set up at $INSTALL_DIR"
}

make_executable() {
    if [ -f "./neuron.sh" ]; then
        # make scripts executable
        chmod +x ./neuron.sh
    else
        log ".satori folder not found. Please unzip the Satori archive first."
    fi
}

install_service() {
    CURRENT_DIR=$(pwd)
    SERVICE_FILE="$CURRENT_DIR/satori.service"
    CURRENT_USER=$(whoami)
    # give user permission to run docker without sudo
    if groups $USER | grep -q docker; then
        log "User has docker permissions."
    else
        log "Giving user docker permissions. Please try again."
        sudo groupadd docker
        sudo usermod -aG docker $CURRENT_USER
        newgrp docker
    fi
    # Updating the User and Group in the satori.service file
    sed -i "s/#User=.*/User=$CURRENT_USER/" $SERVICE_FILE
    # Updating the WorkingDirectory path
    sed -i "s|WorkingDirectory=.*|WorkingDirectory=$CURRENT_DIR|" $SERVICE_FILE
    # install service
    sudo cp satori.service /etc/systemd/system/satori.service
    sudo systemctl daemon-reload
    sudo systemctl enable satori.service
    sudo systemctl start satori.service
    # Check if everything went well
    if groups $USER | grep -q docker && [ -f "/etc/systemd/system/satori.service" ] && systemctl status satori.service &> /dev/null; then
        log "satori.service has been updated with User, Group, and WorkingDirectory path."
        log "install_service.sh completed successfully."
    else
        log "failed to install service, please do so manually."
    fi
}

welcome
log "setting up directories"
setup_directory
log "making scripts executable"
make_executable
log "installing service"
install_service
log "done"
