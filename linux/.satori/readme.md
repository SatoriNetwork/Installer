# installing Satori

### step -1. install docker

If you haven't already, install docker.
Follow the instructions at https://docs.docker.com/desktop/install/linux-install/
Be sure to give docker permissions to your user account.

### step 0. download and unzip Satori for linux

If you haven't already, you'll need to get satori from Satorinet.io.
You can unzip it into your home directory or where ever you want satori installed.
Here's how you can using the terminal.

First you'll need `zip` and `unzip` and `wget` if you don't have them already.

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

```
cd ~
wget -P ~/ https://satorinet.io/static/download/satori.zip
unzip ~/satori.zip
rm satori.zip
```

now you should see this folder: `~/.satori`

### step 1. install dependancies

**automated:**
```
sudo bash install.sh
```

**manual:**
```
cd /.satori
sudo chmod +x ./neuron.sh
sudo chmod +x ./satori.py
sudo python3 -m venv "./satorienv"
sudo source "./satorienv/bin/activate"
sudo pip install -r "./requirements.txt"
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