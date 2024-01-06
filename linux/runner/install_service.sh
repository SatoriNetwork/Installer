#!/bin/bash
sudo cp $HOME/.satori/satori.service /etc/systemd/system/satori.service
sudo systemctl daemon-reload
sudo systemctl enable satori.service
sudo systemctl start satori.service