#!/bin/bash

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo cp /home/pi/clockjr/wififiles/dhcpcd.conf /etc/dhcpcd.conf
sudo cp /home/pi/clockjr/wififiles/interfaces /etc/network/interfaces
sudo service dhcpcd restart
sudo ifdown wlan0
sudo ifup wlan0
sudo service hostapd start
sudo service dnsmasq start
