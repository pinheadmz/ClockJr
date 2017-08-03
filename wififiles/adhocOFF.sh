#!/bin/bash

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo systemctl stop dhcpcd

sudo cp /home/pi/clockjr/wififiles/dhcpcd.conf.old /etc/dhcpcd.conf
sudo cp /home/pi/clockjr/wififiles/interfaces.old /etc/network/interfaces
sudo systemctl start dhcpcd
sudo ifdown wlan0
sudo ifup wlan0
