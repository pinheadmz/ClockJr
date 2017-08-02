import os

try:
	cmdfile = open("/home/pi/clockjr/commands/.wifi","r")
except:
	quit()

command = cmdfile.read()
print "WiFi info received: " + command

try:
	with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as wpafile:
		wpafile.write(command + "\n")
except:
	quit()
	
os.remove("/home/pi/clockjr/commands/.wifi")