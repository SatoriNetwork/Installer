# Satori P2P Setup - Linux

## Prerequisites

1. Install Docker and Docker Compose [ pre-installed with Latest Docker ]
2. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```
3. Restart your session or run:
   ```bash
   newgrp docker
   ```
4. Make sure to disable and stop `satori` service
     - `sudo systemctl disable satori`
     - `sudo systemctl stop satori`
     - `docker rm -f satorineuron` # stops the old container to prevent port collision


## Installation

### 1. Get satori.zip
You can get it from the opensource repository:
```bash
git clone https://github.com/SatoriNetwork/Installer.git
cd satori/zips/linux
```

Or from the website:
```bash
wget -P ~/ https://stage.satorinet.io/static/download/linux/satori.zip
```

### 2. Configure Ports
Edit `config/config.yaml` to set your desired Server and UI ports (default: 24600, 24601).

**Important:** After configuring ports, you must allow these ports through your firewall. See the [Firewall Configuration](#firewall-configuration) section below.

### 3. Add Wallet (Optional)
Place your `wallet.yaml` and `vault.yaml` files in the `wallet` folder if you have an existing wallet.

### 4. Add Old Data and Models (Optional)
If you are using an existing wallet, you can also copy all the data-stream ( containing csv and readme.md ) and model folders  residing inside the `data` and `models\veda`  folder of the old Neuron into the `data` folder and `models\veda` of this directory. [ refer windows readme to see tutorial ]

### 5. Update Docker Compose Configuration
Edit `docker-compose.yaml` and update the volume paths with where the file is located:
```yaml
volumes:
   - ~/satori/linux/config:/Satori/Neuron/config
   - ~/satori/linux/wallet:/Satori/Neuron/wallet
   - ~/satori/linux/data:/Satori/Neuron/data
   - ~/satori/linux/models:/Satori/Neuron/models
```

### 6. Start Application
```bash
docker compose up -d
```

## Managing the Application

### View Logs
```bash
docker logs -f satorineuron
```

### View Individual Application Logs

Satori P2P runs three integrated programs in one container:
- **Neuron** - Collects the Peer info from server, Powers the UI and more
- **Data Server** - Data management
- **Engine** - AI Engine

```cmd
docker exec -it satorineuron bash
cat neuron.log
cat data.log
cat engine.log
```

### Stop Application
```bash
docker compose down
```

## Troubleshooting

### Check Running Containers
```bash
docker ps
```

## Firewall Configuration

**Important:** You must configure your firewall to allow the ports you configured in step 3. Replace 24600 and 24601 with your actual port numbers.

**Ubuntu/Debian (UFW):**
```bash
# Allow localhost to access Satori UI
sudo ufw allow in on lo to any port 24601 proto tcp
# Deny remote access to Satori UI
sudo ufw deny in to any port 24601 proto tcp
# Allow remote access to Satori p2p server
sudo ufw allow 24600/tcp
# Reload and check status
sudo ufw reload
sudo ufw status numbered
```

**Ubuntu/Debian (iptables):**
```bash
# Allow localhost to access Satori UI
sudo iptables -A INPUT -p tcp -s 127.0.0.1 --dport 24601 -j ACCEPT
# Drop all other traffic to Satori UI
sudo iptables -A INPUT -p tcp --dport 24601 -j DROP
# Allow remote traffic to access Satori p2p server
sudo iptables -I INPUT -p tcp --dport 24600 -j ACCEPT
sudo iptables-save
sudo iptables -L -n --line-numbers
```

**CentOS/RHEL/Rocky Linux (firewalld):**
```bash
# Allow localhost to access Satori UI
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="127.0.0.1" port port="24601" protocol="tcp" accept'
# Drop all other traffic to Satori UI
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port port="24601" protocol="tcp" drop'
# Allow remote traffic to access Satori p2p server
sudo firewall-cmd --permanent --add-port=24600/tcp
sudo firewall-cmd --reload
# Check rules
sudo firewall-cmd --list-all
```

**Photon OS:**
```bash
# Allow localhost to access Satori UI
sudo iptables -A INPUT -p tcp -s 127.0.0.1 --dport 24601 -j ACCEPT
# Drop all other traffic to Satori UI
sudo iptables -A INPUT -p tcp --dport 24601 -j DROP
# Allow remote traffic to access Satori p2p server
sudo iptables -I INPUT -p tcp --dport 24600 -j ACCEPT
# Check and save rules
sudo iptables-save
sudo iptables -L -n --line-numbers
```

### Check Port Usage
```bash
netstat -tlnp | grep :24600
netstat -tlnp | grep :24601
```

### Check Firewall Status
**Ubuntu/Debian (UFW):**
```bash
sudo ufw status
```

**CentOS/RHEL/Rocky Linux:**
```bash
sudo firewall-cmd --list-ports
```
