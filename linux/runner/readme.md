# installing Satori

(copy and paste the following 'automated' or 'manual' commands into your terminal)

### step 1. install dependancies

**automated:**
```
sudo bash install.sh
```

**manual:**
```
python3 -m venv satori
source satori/bin/activate
python3 -m pip install -r requirements.txt
```

### step 2. set up a service to keep Satori running

**automated:**
```
sudo bash install_service.sh
```

**manual (preferred):**
It is advised to run the service as a user rather than 'root' but you'll need to ensure that the user has docker privilages. You can give docker privilages to a user with this commands:
```
sudo usermod -aG docker username
newgrp docker
```
then logout and login.

If you want to run the service as a non-root user, uncomment and replace 'username' and 'groupname' in the satori.service file.

```
sudo cp satori.service /etc/systemd/system/satori.service
sudo systemctl daemon-reload
sudo systemctl enable satori.service
sudo systemctl start satori.service
```


**alternative:** run satori on login
```
chmod +x ~/.satori.sh
echo "bash ~/.satori.sh" >> ~/.bashrc
source ~/.bashrc
```