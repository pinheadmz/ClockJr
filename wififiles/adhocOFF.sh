#!/bin/bash

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo systemctl stop dhcpcd

sudo cp ./dhcpcd.conf.old /etc/dhcpcd.conf
sudo cp ./interfaces.old /etc/network/interfaces
sudo systemctl start dhcpcd
sudo ifdown wlan0
sudo ifup wlan0
