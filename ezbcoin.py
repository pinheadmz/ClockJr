import atexit
import math
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import requests

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

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

# clear screen on exit
def cleanup():
	disp.clear()
	disp.display()
atexit.register(cleanup)

# Print text
print('Printing to OLED! Ctrl+C to stop...')
oldHeight = 0
while True:
	# get bitcoin info and define text
	info = requests.get('http://x:0123@127.0.0.1:8332/').json()
	latestHeight = info['chain']['height']
	latestHash = info['chain']['tip']

	if latestHeight != oldHeight:
		params = {"method": "getblockheader", "params": [latestHash]}
		header = requests.post('http://x:0123@127.0.0.1:8332/', json=params).json()
		latestVersion = hex(header['result']['version'])[2:]
		# woha!
		draw.rectangle((0,0,width,height), outline=100, fill=255)
		m = "NEW BLOCK!"
		m_width, m_height = draw.textsize(m, font=font)
		draw.text( ((width - m_width) / 2, (height - m_height) / 2), m, font=font, fill=0)
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
	time.sleep(10)
