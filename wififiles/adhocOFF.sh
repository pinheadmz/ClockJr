#!/bin/bash

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
sudo cp ./dhcpcd.conf.old /etc/dhcpcd.conf
sudo cp ./interfaces.old /etc/network/interfaces
sudo service dhcpcd restart
sudo ifdown wlan0
sudo ifup wlan0
