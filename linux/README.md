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

### 1. Clone Repository
```bash
git clone https://github.com/SatoriNetwork/Installer.git
cd satori-p2p/linux
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
   - ~/satori-p2p/linux/config:/Satori/Neuron/config
   - ~/satori-p2p/linux/wallet:/Satori/Neuron/wallet
   - ~/satori-p2p/linux/data:/Satori/Neuron/data
   - ~/satori-p2p/linux/models:/Satori/Neuron/models
```

### 6. Start Application
```bash
docker compose up -d
```

## Managing the Application

### View Logs
```bash
docker logs -f satorip2p
```

### View Individual Application Logs

Satori P2P runs three integrated programs in one container:
- **Neuron** - Collects the Peer info from server, Powers the UI and more
- **Data Server** - Data management
- **Engine** - AI Engine

```cmd
docker exec -it satorip2p bash
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
sudo ufw allow 24600/tcp
sudo ufw allow 24601/tcp
sudo ufw reload
```

**Ubuntu/Debian (iptables):**
```bash
sudo iptables -I INPUT -p tcp --dport 24600 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 24601 -j ACCEPT
sudo iptables-save
```

**CentOS/RHEL/Rocky Linux (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=24600/tcp
sudo firewall-cmd --permanent --add-port=24601/tcp
sudo firewall-cmd --reload
```

**Photon OS:**
```bash
sudo iptables -I INPUT -p tcp --dport 24600 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 24601 -j ACCEPT
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
