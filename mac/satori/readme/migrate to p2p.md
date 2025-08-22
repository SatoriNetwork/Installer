# Steps to Migrate a Satori Legacy Neruon to a Satori Peer-2-Peer Neuron by shaners,
## 1) Disable Existing Service
```
sudo systemctl disable satori.service
```

## 2) Stop Existing Service
```
sudo systemctl stop satori.service
```

## 3) Stop Existing Container
```
docker stop satorineuron
```

## 4) Delete Existing Images
```
docker rmi $(docker images -q) -f
```

## 5) Download, Install Updates for and Reboot System
```
apt update
apt upgrade -y
reboot
```

## 6) Run Docker Commands
```
sudo usermod -aG docker $USER
newgrp docker
```

## 7) Run Firewall & Port Commands
Enter each IP Table command in order (In case of error, reset IP Table with `iptables -F`)
Each Neuron sharing hardware requires two dedicated ports (Ex: Neuron_One ports `24600/24601`, Neuron_Two ports `24602/24603`, etc)
```
sudo iptables -A INPUT -p tcp --dport 24600 -j ACCEPT
sudo iptables -A INPUT -p tcp -s 127.0.0.1 --dport 24601 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 24601 -j DROP
sudo iptables-save

sudo ufw allow 24600/tcp
sudo ufw allow 24601/tcp
sudo ufw reload
```

## 8) Rename Existing Folder
```
mv satori/ satori-original/
```

## 9) Create P2P Folder
```
mkdir satori/
```

## 10) Copy and Paste Existing Folders into P2P Folder
Delete huggingface/ folder found inside `satori/models/` after copying existing folders to P2P folder with `rm satori/models/huggingface -r`
```
cp satori-original/config/ -r satori/
cp satori-original/wallet/ -r satori/
cp satori-original/data/ -r satori/
cp satori-original/models/ -r satori/
```

## 11) Navigate into P2P Folder and Edit Config File
```
cd ~/satori
nano config/config.yaml
```

## 12) Copy and Paste into Config File 
Remove existing headless setting
Each Neuron sharing hardware requires two dedicated ports (Ex: Neuron_One ports `24600/24601`, Neuron_Two ports `24602/24603`, etc)
```
engine version: v2
mining mode: true
prediction stream: null
server ip: 0.0.0.0
server port: 24600
ui port: 24601
```
Optional Config Settings
neuron lock hash only required if `neuron lock enabled: true` in `config.yaml`
```
disable restart: true or false
logging level: debug
neuron lock enabled: true or false
neuron lock hash: <create random hash>
reward address: <paste address>
```

## 13) Save Config File
```
nano config/config.yaml
```

## 14) Create Docker File
```
nano docker-compose.yaml
```

## 15) Copy and Paste into Docker File
Edit cpus and memory resource limits as needed
```
services:
  satori:
    image: satorinet/satorineuron:p2p
    container_name: satorineuron
    restart: unless-stopped
    network_mode: "host"
    volumes:
      - ~/satori/config:/Satori/Neuron/config
      - ~/satori/wallet:/Satori/Neuron/wallet
      - ~/satori/data:/Satori/Neuron/data
      - ~/satori/models:/Satori/Neuron/models
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

## 16) Save Docker File
```
nano docker-compose.yaml
```

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
Enter each IP Table command in order (In case of error, reset IP Table with `iptables -F` )
Each Neuron sharing hardware requires two dedicated ports (Ex: Neuron_One ports `24600/24601`, Neuron_Two ports `24602/24603`, etc)
Delete huggingface/ folder found inside `satori/models/` after copying existing folders to P2P folder with `rm satori/models/huggingface -r`
Remove existing headless setting from `config.yaml`
neuron lock hash only required if `neuron lock enabled: true` in `config.yaml`
Edit cpus and memory resource limits as needed in `docker-compose.yaml`
To stop Neuron, navigate into `cd ~/satori/` and run `docker compose down`

