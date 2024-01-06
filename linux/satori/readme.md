# installing Satori

(copy and paste the following 'automated' or 'manual' commands into your terminal)

### step -1. install docker

If you haven't already, install docker.
Follow the instructions at https://docs.docker.com/desktop/install/linux-install/
Be sure to give docker permissions to your user account.

### step 0. download and unzip Satori for linux

If you haven't already, which you probably have, you'll need to get satori from Satorinet.io.
make sure you unzip it into your home directory like this `~/.satori`.
Here's how you can using the commandline.

You'll need zip and unzip and wget if you don't have them already.

for Debian/Ubunto-based systems use:
```
sudo apt-get update
sudo apt-get install zip unzip wget curl
```
for Red Hat/CentOS-based systems use:
```
sudo yum update
sudo yum install zip unzip wget curl
```

Then you can download and unzip Satori.

**manual:**
```
wget -P ~/ https://satorinet.io/static/download/satori.zip
unzip ~/satori.zip -d ~/.satori
```

### step 1. install dependancies

**automated:**
```
sudo bash install.sh
```

**manual:**
```
sudo chmod +x $HOME/.satori/neuron.sh
sudo chmod +x $HOME/.satori/satori.py
sudo python3 -m venv "$HOME/.satori/env"
sudo source "$HOME/.satori/env/bin/activate"
sudo pip install -r "$HOME/.satori/requirements.txt"
sudo deactivate
```

### step 2. set up a service to keep Satori running

**important:**
It is advised to run the service as a user rather than 'root'. You'll need to ensure that the user has docker privilages. If you haven't already, you can give docker privilages to a user with this commands:
```
sudo usermod -aG docker username
newgrp docker
```
then logout and login.

Now modify the satori.service file. If you want to run the service as a non-root user, uncomment and replace 'username' and 'groupname' in the satori.service file. You can modify the file with the commands `nano` or `vi`, use `:wq` to write and quit vim:
```
vi $HOME/.satori/satori.service
```

**automated:**
```
sudo bash install_service.sh
```

**manual:**
```
sudo cp $HOME/.satori/satori.service /etc/systemd/system/satori.service
sudo systemctl daemon-reload
sudo systemctl enable satori.service
sudo systemctl start satori.service
```

### step 3. verify it's up and running occasionally

Try to keep it runnning as much as you can. Satori data streams that are active every day retain their sanctioned status and are eligible for rewards. Satori Neurons that are up and running every month remain activate and eligible for rewards.

```
sudo systemctl status satori.service
```