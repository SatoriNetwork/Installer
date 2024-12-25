#####################
# Installing Satori #
#####################

Here we outline 4 easy steps to install Satori on Linux, the first two of which you have probably already completed. There are automated scripts that run the remaining two steps, or you can run each command manually.

## Step -1. Istall docker

If you haven't already, install the Docker Engine.
Ubuntu: https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
Debian: https://docs.docker.com/engine/install/debian/#install-using-the-repository
Fedora: https://docs.docker.com/engine/install/fedora/#install-using-the-repository
Or follow the instructions at https://docs.docker.com/desktop/install/linux-install/

## Step 0. Download and unzip Satori for linux

If you haven't already, you'll need to get satori from Satorinet.io.
You can unzip it into your home directory or where ever you want satori installed.
Here's how you can using the terminal.

First you'll need `zip` and `unzip` and `wget` if you don't have them already.

For Debian/Ubunto-based systems use:
```
sudo apt-get update
sudo apt-get install zip unzip wget curl
```

For Red Hat/CentOS-based systems use:
```
sudo yum update
sudo yum install zip unzip wget curl
```

Then you can download and unzip Satori:
```
cd ~
wget -P ~/ https://satorinet.io/static/download/satori.zip
unzip ~/satori.zip
rm ~/satori.zip
cd ~/.satori
```

Now you should have this folder: `~/.satori`

## Step 1. install runner script and service

**automated:**
```
bash install.sh
```

**manual:**
```
chmod +x ./neuron.sh
# see install.sh script for installing service
```

## Step 2. verify it's up and running occasionally

Try to keep it runnning as much as you can. Satori data streams that are active every day retain their sanctioned status and are eligible for rewards. Satori Neurons that are up and running every month remain activate and eligible for rewards.

```
sudo systemctl status satori.service
```

You can even watch the logs:
```
journalctl -fu satori.service
```
