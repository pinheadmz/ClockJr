import os
import socket

def addWifi():
	try:
		cmdfile = open("/home/pi/clockjr/commands/.wifi","r")
	except:
		print "No WiFi info received"
		return False

	command = cmdfile.read()
	print "WiFi info received: " + command

	try:
		with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as wpafile:
			wpafile.write(command + "\n")
	except:
		print "Error writing to wpa_supplicant.conf"
		return False
	
	os.remove("/home/pi/clockjr/commands/.wifi")
	return True
	
def checkInternet():
	 """
	 Host: 8.8.8.8 (google-public-dns-a.google.com)
	 OpenPort: 53/tcp
	 Service: domain (DNS/TCP)
	 """
	 host="8.8.8.8"
	 port=53
	 timeout=3
	 try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	 except Exception as ex:
		print ex.message
		return False