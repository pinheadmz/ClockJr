import atexit
import math
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import requests
import hashlib 
import re
import psutil
import os
import sys
import json

sys.path.append("/home/pi/clockjr/wififiles")
from addwifi import *

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from neopixel import *

### OLED DISPLAY CONFIG ###
# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0
# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

### OLED DISPLAY INIT ###
# Initialize library.
disp.begin()
# Get display width and height.
width = disp.width
height = disp.height
# Clear display.
disp.clear()
disp.display()
# Create image buffer.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (width, height))
# Load default font.
font = ImageFont.load_default()
# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as this python script!
# Some nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)
# Create drawing object.
draw = ImageDraw.Draw(image)

### NEOPIXEL CONFIG ###
# LED strip configuration:
LED_COUNT      = 40      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 10     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

### NEOPIXEL INIT ###
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
# Intialize the library (must be called once before other functions).
strip.begin()

### CLOCK Jr. ###
DISPLAYS = True

# clear screen on exit
def cleanup():
	disp.clear()
	disp.display()
	for i in range(0, strip.numPixels(), 1):
		strip.setPixelColor(i, Color(0, 0, 0))
	strip.show()
atexit.register(cleanup)

# is bcoin running?
def isBcoin():
	isit = False
	for pid in psutil.pids():
		try:
			if "bcoin" in psutil.Process(pid).name():
				isit = True
		except:
			continue
	return isit

# restart bcoin if its not running
def checkAndRestartBcoin():
	print('checking for bcoin...')
	if not isBcoin():
		print('bcoin is not running, restarting...')
		OLEDtext("Starting bcoin...")
		os.system('su -c "bcoin --prune --daemon --listen=false --selfish" - pi')
		print('giving bcoin a 30 sec head start...')
		for i in range(30):
			print(30-i)
			OLEDtext("Waiting for bcoin... " + str(30-i))
			time.sleep(1)
	else:
		print('bcoin process found!')
		OLEDtext("bcoin is running!")
	return True

# Neopixel rainbow cycle
def clearNeopixels():
	for i in range(0, strip.numPixels(), 1):
		strip.setPixelColor(i, Color(0, 0, 0))

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)
def rainbowCycle(strip, wait_ms=5, iterations=1):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)
	clearNeopixels()
	strip.show()

def OLEDtext(text):
	# Clear OLED image buffer by drawing a black filled box.
	draw.rectangle((0,0,width,height), outline=0, fill=0)
	# Stop here if displays are OFF!
	if not DISPLAYS:
		disp.image(image)
		disp.display()
		return True
	
	# Enumerate characters and draw them to OLED
	x = 0
	y = 0
	for i, c in enumerate(text):
		# get char dimensions
		char_width, char_height = draw.textsize(c, font=font)
		# advance to edge but don't cut off any chars, then new line to bottom
		if x + char_width > width:
			y += char_height # i guess we assume all chars are similar height?
			x = 0
		if x > width and y > height:
			break
		# Draw text.
		draw.text((x, y), c, font=font, fill=255)
		# Increment x position based on chacacter width.
		x += char_width
	# push image to screen
	rotimage=image.rotate(180)
	disp.image(rotimage)
	disp.display()

# read php-ui-generated files from commands folder
def readCommands():
	try:
		cmdfile = open("/home/pi/clockjr/commands/.clockjrcommand","r")
	except:
		return False
	
	command = cmdfile.read()
	print "Web UI Command received: " + command
	if command == "P":
		rainbowCycle(strip)
	if command == "O":
		global DISPLAYS
		DISPLAYS = not DISPLAYS
	os.remove("/home/pi/clockjr/commands/.clockjrcommand")
	return True

# get price
def getPriceString():
	try:
		# try coinbase first
		r = requests.get('https://api.coinbase.com/v2/prices/BTC-USD/spot')
		rj = json.loads(r.text)
		price = rj['data']['amount']
		return '%-7s%14.14s' % ('price: ', '${:,.2f}'.format(float(price)))
	except:
		try:
			# try blockchain.info next 
			r = requests.get('https://blockchain.info/ticker')
			rj = json.loads(r.text)
			price = rj['USD']['last']
			return '%-7s%14.14s' % ('price: ', '${:,.2f}'.format(float(price)))
		except:
			# give up getting price
			return '%-7s%14.14s' % ('price: ', 'n/a')

# check for and establish internet connection
def checkAndGetWiFi():
	# give Pi a chance to connect to WiFi, maybe it already has credentials
	for i in range(60):
		if checkInternet():
			return True
		text = '%-21.21s' % ("No internet detected")
		text += '%-21.21s' % ("Switching to ad-hoc")
		text += '%-21.21s' % ("in: " + str (60-i) + " seconds")
		# write text to OLED
		OLEDtext(text)
		time.sleep(1)

	# OK maybe we need some credentials to get internet
	text = '%-21.21s' % ("No internet detected")
	text += '%-21.21s' % ("Starting ad-hoc WiFi")
	text += '%-21.21s' % ("ssid: clockjr")
	text += '%-21.21s' % ("pw:   2themoon")
	text += '%-21.21s' % ("http://192.168.0.1")
	# write text to OLED
	OLEDtext(text)
	os.system("sudo /home/pi/clockjr/wififiles/adhocON.sh")
	while not addWifi():
		time.sleep(5)
	os.system("sudo /home/pi/clockjr/wififiles/adhocOFF.sh")
	text = '%-21.21s' % ("WiFi info received!")
	text += '%-21.21s' % ("Attempting to connect")
	# write text to OLED
	OLEDtext(text)
	# give it a few seconds
	time.sleep(30)

##### Program begin #####
while not checkInternet():
	checkAndGetWiFi()

checkAndRestartBcoin()
print('Clock Jr. starting!')
OLEDtext("Clock Jr. starting!")
blocks = []
priceString = ''

# Main Loop
while True:
	currentTime = int(time.time())

	# get bitcoin info and define text
	try:
		info = requests.get('http://x:0123@127.0.0.1:8332/').json()
	except:
		print("Error:", sys.exc_info()[0])
		checkAndRestartBcoin()
		time.sleep(5)
		continue	
	
	progress = info['chain']['progress']
	latestHeight = info['chain']['height']
	latestHash = info['chain']['tip']
	oldHeight = blocks[-1]['height'] if len(blocks)>0 else 0
	
	if latestHeight != oldHeight:
		# get new block info
		params = {"method": "getblock", "params": [latestHash]}
		try:
			header = requests.post('http://x:0123@127.0.0.1:8332/', json=params).json()
		except:
			print("Error:", sys.exc_info()[0])
			checkAndRestartBcoin()
			time.sleep(5)
			continue	
	
		latestVersion = header['result']['versionHex']
		latestSize = header['result']['size']
		latestCoinbase = header['result']['coinbase']
		# clean up hex from coinbase
		coinbasestring = ""
		for i in xrange(0, len(latestCoinbase)-2, 2):
			c = latestCoinbase[i:i+2]
			cint = int(c, 16)
			if not 126 > cint > 32:
				continue
			coinbasestring += chr(cint)
		extraVersion = ""
		# anything interesting in that coinbase?
		if "/AD" and "/EB" in coinbasestring:
			extraVersion = re.search('/EB[0-9.]+/AD[0-9.]+/', coinbasestring).group(0)
		if "/EXTBLK/" in coinbasestring:
			extraVersion = "/EXTBLK/"
			
		# store up to 40 recent blocks in memory
		if len(blocks)>40:
			blocks.pop(0)
		blocks.append({"height":latestHeight,"hash":latestHash,"coinbase":coinbasestring,"version":latestVersion,"extraVersion":extraVersion,"size":latestSize,"time":currentTime})
		
		# get the price
		priceString = getPriceString()
		
		# party time for new block!
		if DISPLAYS:
			# neopixels party	
			rainbowCycle(strip)
			# OLED party
			draw.rectangle((0,0,width,height), outline=100, fill=255)
			m = "NEW BLOCK!"
			m_width, m_height = draw.textsize(m, font=font)
			draw.text( ((width - m_width) / 2, (height - m_height) / 2), m, font=font, fill=0)
			# Draw the image buffer.
			rotimage=image.rotate(180)
			disp.image(rotimage)
			disp.display()
			time.sleep(2)
		oldHeight = latestHeight
		# debug
		print('--')
		for block in blocks:
			print(block)

	# build sequence for neopixel strip
	blocksPerLED = 2016/16
	blocksElapsedInPeriod = latestHeight%2016
	elapsedPercent = blocksElapsedInPeriod/2016.0
	redness = int(elapsedPercent*255)
	blueness = int((1-elapsedPercent)*255)
	elapsedLEDs = (blocksElapsedInPeriod/blocksPerLED) + 1

	# push to strip!
	clearNeopixels()
	if DISPLAYS:
		# indicate recent blocks around outer neopixel ring
		for block in blocks[::-1]:
			elapsed = currentTime - block['time'] 
			if  elapsed/120 > 23:
				break
			# modulo ffffff or (255, 255, 255) for color
			versionColor = hashlib.md5(str(block['version']) + block['extraVersion']).hexdigest()
			strip.setPixelColor((elapsed/120 + 5)%24, Color(int(versionColor[0:2],16), int(versionColor[2:4],16), int(versionColor[4:6],16)))
		# indicate difficulty adjustment period around inner neopixel ring
		for pixel in range(elapsedLEDs):
			strip.setPixelColor( 39-((pixel+2)%16), Color(redness, 0, blueness))
		
	# paint the neopixel strip
	strip.show()

	# if we're still catching up, print progress
	if progress != 1:
		text = 'bcoin is catching up!'
		text += '%-10s%-9s%-2.1s' % ('progress: ', int(progress*100000000)/1000000.0, '%')
		text += '%-8s%13.13s' % ('height: ', latestHeight)
		# write text to OLED
		OLEDtext(text)
		# don't bother bcoin too much while its syncing
		waitBeforeReloadBcoinInfo = 30
	else:
		# we're synced! print stats	to OLED
		text = priceString
		text += '%-8s%13.13s' % ('height: ', latestHeight)
		text += '%-13s%8.8s' % ('version: ', latestVersion)
		text += '%21.21s' % (extraVersion)
		text += '%-13s%8.8s' % ('size: ', latestSize)
		text += '%-15s%6.6s' % ('next diff adj: ', 2016-blocksElapsedInPeriod)
		# write text to OLED
		OLEDtext(text)
		# bother bcoin a lot if we're synced!
		waitBeforeReloadBcoinInfo = 5
	
	# Pause before requesting info and re-drawing
	for i in range(waitBeforeReloadBcoinInfo * 2):
		# Get user input. Check every 1/2 sec for command. If command, restart whole loop
		if not readCommands():
			time.sleep(0.5)
		else:
			break
