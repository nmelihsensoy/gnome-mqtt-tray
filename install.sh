#!/bin/bash

echo "Python File --------------------------------------------------"
sudo cp -v $PWD/gnome-mqtt-tray.py /usr/bin/;
echo "--------------------------------------------------------------"
echo "Config Folder ------------------------------------------------"
cp -avr $PWD/gnome-mqtt-tray/ ~/.config/gnome-mqtt-tray-config;
echo "--------------------------------------------------------------"
echo "Service File -------------------------------------------------"
sudo cp -v $PWD/gnome-mqtt-tray.service /etc/systemd/system;
echo "--------------------------------------------------------------"

##Enable service
sudo systemctl enable gnome-mqtt-tray;
sudo systemctl start gnome-mqtt-tray;
