#!/bin/bash

# upgrade Process:
# 0. modify Satori/Neuron, make a new image put that image version in here (TAG)
# 1. if scripts/*.py modified, follow instructions within to update the hash
# 2. push Satori/Neuron to github, and satorinet/satorineuron=vX image to docker hub
# 3. modify this file
# 4. using windows linux subsystem (WSL) zip up all contents of satori folder:
# 5. copy to download static folder of Central:
#   ```
#   cd /mnt/c/repos/Satori/Installer/linux
#   rm -rf satori.zip
#   zip -r satori.zip .satori
#   cp /mnt/c/repos/Satori/Installer/linux/satori.zip /mnt/c/repos/Satori/Central/satoricentral/server/static/download/linux/
#   echo "done"
#
#   ```
# 6. push Installer and Central, `cycle` on server

if ! source "$(dirname "$0")/run/linux.sh"; then
    echo "Failed to load linux.sh, running with defaults."
fi

echo "Satori Neuron"

default_welcome() {
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

default_setup_directory() {
    # Define the install directory
    local INSTALL_DIR="$HOME/.satori"
    # Create the necessary directories if they don't already exist
    mkdir -p "$INSTALL_DIR/run"
    mkdir -p "$INSTALL_DIR/wallet"
    mkdir -p "$INSTALL_DIR/config"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/models"
    echo "Directories set up at $INSTALL_DIR"
}

default_start_docker() {
    # Ensure Docker is running and accessible
    if ! docker info >/dev/null 2>&1; then
        echo "Docker is not accessible. Please ensure you have the necessary permissions."
        exit 1
    fi

    # Check if Docker daemon is running, start it if not
    if ! pgrep -x "dockerd" >/dev/null; then
        echo "Starting Docker..."
        sudo systemctl start docker
        until docker info >/dev/null 2>&1; do
            echo "Waiting for Docker to start..."
            sleep 5
        done
    fi
}

default_remove_dangling_images() {
    echo "Removing dangling images for satorinet/satorineuron..."
    # Get a list of dangling image IDs for the specified reference
    local dangling_images
    dangling_images=$(docker images -q -f "reference=satorinet/satorineuron" -f "dangling=true")
    # If there are any dangling images, remove them
    if [[ -n "$dangling_images" ]]; then
        docker rmi $dangling_images
        echo "Dangling images removed."
    else
        echo "No dangling images found."
    fi
}

default_get_config_value() {
    local config_path="$1"
    local key="$2"
    local default_value="prod"
    # Check if the config file exists
    if [[ -f "$config_path" ]]; then
        # Read the file line by line
        while IFS= read -r line; do
            # Check if the line starts with the specified key
            if [[ "$line" == "$key:"* ]]; then
                # Extract and return the value after the key
                echo "${line#$key:}" | xargs
                return
            elif [[ "$line" == "$key="* ]]; then
                # For RUNMODE case
                echo "${line#$key=}" | xargs
                return
            fi
        done < "$config_path"
    fi
    # Default value if not found
    echo "$default_value"
}

default_run_container() {
    echo "Starting Satori Neuron container..."
    # Define the config path and get the ENV value
    local config_path="$HOME/.satori/config/config.yaml"
    local env_path="$HOME/.satori/config/.env"
    local env_value=$(default_get_config_value "$config_path" "env")
    local run_value=$(default_get_config_value "$env_path" "RUNMODE")
    # Stop any running container and pull the latest image
    docker stop satorineuron >/dev/null 2>&1 || true
    docker pull satorinet/satorineuron:latest
    default_remove_dangling_images
    # Open the browser
    xdg-open http://localhost:24601 >/dev/null 2>&1 || echo "Unable to open browser."
    # Determine the port mapping based on run_value
    # should 127.0.0.1:24601 be the new headless mode?
    local port_mapping
    if [[ "$run_value" == "worker" ]]; then
        port_mapping="-p 24600:24600 -p 127.0.0.1:24601:24601"
    else
        port_mapping="-p 24600:24600 -p 24601:24601"
    fi
    # Run the container with the dynamically determined ENV value
    docker run --rm --name satorineuron $port_mapping \
        -v "$HOME/.satori/run:/Satori/Neuron/run" \
        -v "$HOME/.satori/wallet:/Satori/Neuron/wallet" \
        -v "$HOME/.satori/config:/Satori/Neuron/config" \
        -v "$HOME/.satori/data:/Satori/Neuron/data" \
        -v "$HOME/.satori/models:/Satori/Neuron/models" \
        --env ENV="$env_value" \
        satorinet/satorineuron:latest ./start.sh
    return $?
}

default_handle_exit_code() {
    local exit_code=$1
    case $exit_code in
        0)
            echo "Container exited normally. Shutting down."
            exit 0
            ;;
        1|2)
            echo "Container requested restart. Restarting..."
            ;;
        125)
            echo "Docker daemon error. Exiting."
            exit 125
            ;;
        137)
            echo "Container was killed (likely out of memory). Exiting."
            exit 137
            ;;
        126)
            echo "Command cannot be invoked. Exiting."
            exit 126
            ;;
        127)
            echo "Command not found. Exiting."
            exit 127
            ;;
        130)
            echo "Container terminated by Ctrl+C. Exiting."
            exit 130
            ;;
        143)
            echo "Container received shutdown request. Exiting."
            exit 143
            ;;
        *)
            echo "Unknown error code: $exit_code. Exiting."
            exit $exit_code
            ;;
    esac
}

default_log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

main() {
    if ! welcome; then
        default_welcome
    fi
    if ! setup_directory; then
        default_setup_directory
    fi
    if ! start_docker; then
        default_start_docker
    fi
    while true; do
        if ! default_log "to see logs use command: docker logs -f satorineuron"; then
            default_log "to see logs use command: docker logs -f satorineuron"
        fi
        if ! log "Running Satori Neuron container..."; then
            default_log "Running Satori Neuron container..."
        fi
        if ! run_container; then
            deafult_run_container
        fi
        exit_code=$?
        if ! log "Container exited with code $exit_code."; then
            default_log "Container exited with code $exit_code."
        fi
        if ! handle_exit_code $exit_code; then
            default_handle_exit_code $exit_code
        fi
    done
}

main
