import atexit
import math
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import requests

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

### NEOPIXEL INIT ###
# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
# Intialize the library (must be called once before other functions).
strip.begin()

### CLOCK Jr. ###
# clear screen on exit
def cleanup():
	disp.clear()
	disp.display()
	for i in range(0, strip.numPixels(), 1):
		strip.setPixelColor(i, Color(0, 0, 0))
	strip.show()
atexit.register(cleanup)

# Neopixel rainbow cycle
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
	for i in range(0, strip.numPixels(), 1):
		strip.setPixelColor(i, Color(0, 0, 0))
	strip.show()

# Main Loop
print('Printing to OLED! Ctrl+C to stop...')
oldHeight = 0
while True:
	# get bitcoin info and define text
	info = requests.get('http://x:0123@127.0.0.1:8332/').json()
	latestHeight = info['chain']['height']
	latestHash = info['chain']['tip']

	if latestHeight != oldHeight:
		# testing neopixels	
		rainbowCycle(strip)
		
		params = {"method": "getblockheader", "params": [latestHash]}
		header = requests.post('http://x:0123@127.0.0.1:8332/', json=params).json()
		latestVersion = hex(header['result']['version'])[2:]
		# woha!
		draw.rectangle((0,0,width,height), outline=100, fill=255)
		m = "NEW BLOCK!"
		m_width, m_height = draw.textsize(m, font=font)
		draw.text( ((width - m_width) / 2, (height - m_height) / 2), m, font=font, fill=0)
		oldHeight = latestHeight
		# Draw the image buffer.
		disp.image(image)
		disp.display()
		time.sleep(2)
		
	# Clear image buffer by drawing a black filled box.
	draw.rectangle((0,0,width,height), outline=0, fill=0)

	text =  'bcoin version:       '
	text +=  '%21.21s' % (info['version'])
	text += 'Latest block info:   '
	text += '%-8s%13.13s' % ('height: ', latestHeight)
	text += '%-13.13s%8.8s' % ('version: ', latestVersion)
	text += '                     '

	# Enumerate characters and draw them
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
	# Draw the image buffer.
	disp.image(image)
	disp.display()
	
	# Pause before requesting info and re-drawing
	time.sleep(2)
