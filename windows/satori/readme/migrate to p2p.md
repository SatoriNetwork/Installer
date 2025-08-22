# Steps to Migrate a Satori Legacy Neuron to a Satori Peer-2-Peer Neuron - Windows

## 1) Stop Existing Startup Batch File
Remove the Satori startup batch file from the Windows Startup folder:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
```
Delete any `satori.bat` or similar batch files that start the legacy Satori Neuron.

## 2) Stop Existing Container
```
docker stop satorineuron
```

## 3) Remove Existing Container
```
docker rm satorineuron
```

## 4) Delete Existing Images
```
docker rmi $(docker images -q) -f
```

## 5) Update Docker Desktop
Ensure Docker Desktop is up to date and restart it if needed.

## 6) Enable Host Networking in Docker Desktop
- Open Docker Desktop
- Go to Settings → Resources → Network
- Enable "Use host networking"
- Restart Docker Desktop

## 7) Configure Windows Firewall
Open PowerShell as Administrator and run these commands:
Each Neuron sharing hardware requires two dedicated ports (Ex: Neuron_One ports `24600/24601`, Neuron_Two ports `24602/24603`, etc)
```powershell
# Allow localhost to access Satori UI
New-NetFirewallRule -DisplayName "Satori UI Localhost" -Direction Inbound -Protocol TCP -LocalPort 24601 -RemoteAddress 127.0.0.1 -Action Allow

# Block all remote access to Satori UI
New-NetFirewallRule -DisplayName "Satori UI Block Remote" -Direction Inbound -Protocol TCP -LocalPort 24601 -RemoteAddress Any -Action Block

# Allow remote access to Satori P2P server
New-NetFirewallRule -DisplayName "Satori P2P Server" -Direction Inbound -Protocol TCP -LocalPort 24600 -Action Allow
```

## 8) Rename Existing Legacy Folder
Navigate to the legacy Satori installation location (typically in AppData):
```
%APPDATA%\local\Satori\
```
Rename the existing folder:
```
ren "%APPDATA%\local\Satori" "Satori-original"
```

## 9) Create New P2P Folder
Create the new Satori P2P folder:
```
mkdir "%USERPROFILE%\satori"
```

## 10) Copy and Paste Existing Folders into P2P Folder
Delete huggingface/ folder found inside `satori/models/` after copying existing folders to P2P folder
```
xcopy "%APPDATA%\local\Satori-original\config" "%USERPROFILE%\satori\config" /E /I
xcopy "%APPDATA%\local\Satori-original\wallet" "%USERPROFILE%\satori\wallet" /E /I
xcopy "%APPDATA%\local\Satori-original\data" "%USERPROFILE%\satori\data" /E /I
xcopy "%APPDATA%\local\Satori-original\models" "%USERPROFILE%\satori\models" /E /I
```

Remove the huggingface folder:
```
rmdir /S /Q "%USERPROFILE%\satori\models\huggingface"
```

## 11) Navigate into P2P Folder and Edit Config File
```
cd "%USERPROFILE%\satori"
notepad config\config.yaml
```

## 12) Copy and Paste into Config File 
Remove existing headless setting
Each Neuron sharing hardware requires two dedicated ports (Ex: Neuron_One ports `24600/24601`, Neuron_Two ports `24602/24603`, etc)
```yaml
engine version: v2
mining mode: true
prediction stream: null
server ip: 0.0.0.0
server port: 24600
ui port: 24601
```
Optional Config Settings
neuron lock hash only required if `neuron lock enabled: true` in `config.yaml`
```yaml
disable restart: true or false
logging level: debug
neuron lock enabled: true or false
neuron lock hash: <create random hash>
reward address: <paste address>
```

## 13) Save Config File
Save the file in Notepad and close it.

## 14) Create Docker Compose File
```
notepad docker-compose.yaml
```

## 15) Copy and Paste into Docker Compose File
Edit cpus and memory resource limits as needed
```yaml
services:
  satori:
    image: satorinet/satorineuron:p2p
    container_name: satorineuron
    restart: unless-stopped
    network_mode: "host"
    volumes:
      - ${USERPROFILE}/satori/config:/Satori/Neuron/config
      - ${USERPROFILE}/satori/wallet:/Satori/Neuron/wallet
      - ${USERPROFILE}/satori/data:/Satori/Neuron/data
      - ${USERPROFILE}/satori/models:/Satori/Neuron/models
    environment:
      - ENV=prod
    deploy: # change or remove as desired 
      resources: # this limits the resources
        limits:
          cpus: "1.3"
          memory: "3.5g"
    stdin_open: true
    tty: true
    pull_policy: always
    entrypoint: ["bash", "/Satori/Neuron/satorineuron/web/start.sh"]
```

## 16) Save Docker Compose File
Save the file in Notepad and close it.

## 17) Run Container
```
docker compose up -d
```

## 18) Check Logs
```
docker logs -f satorineuron
```
```
docker exec -it satorineuron bash
cat neuron.log
cat data.log
cat engine.log
```

## Important Extras
Each Neuron sharing hardware requires two dedicated ports (Ex: Neuron_One ports `24600/24601`, Neuron_Two ports `24602/24603`, etc)
Delete huggingface/ folder found inside `satori/models/` after copying existing folders to P2P folder
Remove existing headless setting from `config.yaml`
neuron lock hash only required if `neuron lock enabled: true` in `config.yaml`
Edit cpus and memory resource limits as needed in `docker-compose.yaml`
To stop Neuron, navigate into `cd "%USERPROFILE%\satori"` and run `docker compose down`

## Windows-Specific Notes
- The legacy Satori was typically installed in `%APPDATA%\local\Satori\`
- The new P2P version uses `%USERPROFILE%\satori\` (typically `C:\Users\YourUsername\satori\`)
- Windows uses `%USERPROFILE%` instead of `~` for the home directory
- Use `notepad` instead of `nano` for editing files
- Use `xcopy` with `/E /I` flags for recursive directory copying
- Use `rmdir /S /Q` for recursive directory deletion
- Windows Firewall rules are configured via PowerShell instead of iptables

