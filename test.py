import sys
import os
import time
sys.path.append("/home/pi/clockjr/wififiles")
from addwifi import *

print "Starting up..."

if not checkInternet():
	print "No internet detected, attempting to start ad-hoc WiFi"
	print "ssid: clockjr"
	print "pw:   2themoon"
	print "http://192.168.0.1"
	os.system("sudo /home/pi/clockjr/wififiles/adhocON.sh")
	while not addWifi():
		time.sleep(5)
	print "Attempting to connect to WiFi"
	os.system("sudo /home/pi/clockjr/wififiles/adhocOFF.sh")

print "Done!"