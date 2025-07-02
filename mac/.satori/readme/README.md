# Satori P2P Setup - macOS

## Prerequisites

1. Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
2. Enable host networking in Docker Desktop [ refer windows readme to see tutorial ]:
   - Open Docker Desktop
   - Go to Settings → Resources → Network
   - Enable "Use host networking"
   - Restart Docker Desktop


## Installation

### 1. Get satori.zip
You can get it from the opensource repository:
```bash
git clone https://github.com/SatoriNetwork/Installer.git
cd satori/zips/mac
```

Or from the website:
```bash
wget -P ~/ https://stage.satorinet.io/static/download/mac/satori.zip
```

### 2. Configure Ports
Edit `config/config.yaml` to set your desired Server and UI ports (default: 24600, 24601).

### 3. Add Wallet (Optional)
Place your `wallet.yaml` and `vault.yaml` files into the `wallet` folder if you have an existing wallet.

### 4. Add Old Data and Models (Optional)
If you are using an existing wallet, you can also copy all the data-stream ( containing csv and readme.md ) and model folders  residing inside the `data` and `models\veda`  folder of the old Neuron into the `data` folder and `models\veda` of this directory. [ refer windows readme to see tutorial ]

### 5. Update Docker Compose Configuration
Edit `docker-compose.yaml` and update the volume paths with where the file is located:
```yaml
volumes:
   - ~/satori/mac/config:/Satori/Neuron/config
   - ~/satori/mac/wallet:/Satori/Neuron/wallet
   - ~/satori/mac/data:/Satori/Neuron/data
   - ~/satori/mac/models:/Satori/Neuron/models
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

```bash
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

### Edit pf configuration
Backup and edit:
```bash
sudo cp /etc/pf.conf /etc/pf.conf.bak
sudo nano /etc/pf.conf
```
paste:
```pf
# Allow localhost to access Satori UI
pass in quick on lo0 proto tcp from 127.0.0.1 to any port 24601

# Block all remote access to Satori UI
block in proto tcp from any to any port 24601

# Allow remote access to Satori p2p server
pass in proto tcp from any to any port 24600
```
Apply the config:
```bash
# Enable pf if it's not running
sudo pfctl -e

# Reload the config
sudo pfctl -f /etc/pf.conf

# Verify rules are loaded
sudo pfctl -sr
```

### Check Port Usage
```bash
netstat -an | grep :24600
netstat -an | grep :24601
```

### Check Docker Service
```bash
docker info
```

## Firewall Configuration

macOS typically doesn't block Docker containers when host networking is enabled. The built-in firewall generally doesn't interfere with Docker host networking.

If you're using third-party firewall software like Little Snitch, you may need to create rules to allow connections on your configured ports.

