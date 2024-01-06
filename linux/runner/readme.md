# installing Satori

(copy and paste the following 'automated' or 'manual' commands into your terminal)

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

**optional:**
It is advised to run the service as a user rather than 'root' but you'll need to ensure that the user has docker privilages. You can give docker privilages to a user with this commands:
```
sudo usermod -aG docker username
newgrp docker
```
then logout and login.

If you want to run the service as a non-root user, uncomment and replace 'username' and 'groupname' in the satori.service file.

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